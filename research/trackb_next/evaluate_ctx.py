"""Pre-registered evaluation of the RUN_PRESET "ctx" outputs (kill test in research/trackb_next/RESULT.md).

    .venv/bin/python research/trackb_next/evaluate_ctx.py --root <folder holding val/ and test/ of trackb_ctx>
        [--lovo]          # criterion 4 (member-set selection inside leave-one-video-out, family rules applied)

Validation labels are read only to score; facts = research/trackb_dense/out/fact_labels.csv (exact stated values in
test scene families). Reference = cvq_geo of trackb_v1 (SAM 2 prompted by Qwen3-VL boxes, CaW fallback), taken from
the full-resolution test run where the validation question is also a test question, else from the 480p val run.
Criteria (all must hold for one method):
 1. val macro MRA >= cvq_geo + 0.030 and clip-bootstrap 90% CI lower bound of the delta > 0
 2. size / distance target rows: item mean >= cvq_geo + 0.05
 3. fact rows the method changes vs cvq_geo: mean item change >= 0, AND the method answers >= 90% of the fact rows
 4. (--lovo) LOVO macro of the per-category member-set search with the new methods >= LOVO of the same search
    without them (old 4 + cvq_geo) + 0.010
Amendment 2026-10-15 (before any ctx output existed; tightening only, from the independent VERIFY.md): criterion 4
baseline changed from v3's old-4 search (.5793, which cvq_geo alone beats) to old 4 + cvq_geo; criterion 3 requires
fact coverage; cvqcx_geo added to the pre-declared methods.
"""
from __future__ import annotations

import argparse
import itertools
import math
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "research" / "trackb_dense"))
warnings.filterwarnings("ignore")

from qp import postprocess as pp  # noqa: E402
from qp.mra import item_scores  # noqa: E402
from tbcommon import RUN, questions  # noqa: E402

CATS = ("S2", "D2", "S3", "D3")
NEW = {"ta_geo": "ta/geometry.csv", "tacx_geo": "tacx/geometry.csv", "samcx_geo": "samcx/geometry.csv",
       "cvqcx_geo": "cvqcx/geometry.csv", "tasam_geo": "tasam/geometry.csv", "ta_direct": "ta/direct.csv"}
PRIMARY = ("ta_geo", "tacx_geo", "samcx_geo", "ta_direct", "cvqcx_geo")   # pre-declared (cvqcx added 10-15)
FACTS = ROOT / "research" / "trackb_dense" / "out" / "fact_labels.csv"


def read(path: Path, ids) -> np.ndarray:
    if not Path(path).exists():
        return np.full(len(ids), np.nan)
    d = pd.read_csv(path)
    s = pd.to_numeric(d.set_index(d.columns[0])["parsed_value"], errors="coerce")
    s = s.where(np.isfinite(s) & (s > 0))
    return s.reindex(list(ids)).to_numpy(float)


def items(pred, gt) -> np.ndarray:
    return np.nan_to_num(np.asarray(item_scores(np.asarray(pred, float), np.asarray(gt, float)), float))


def macro(it, cat) -> float:
    return float(np.mean([it[cat == c].mean() for c in CATS]))


def boot(a, b, cat, vid, n=2000, seed=0):
    vids = np.unique(vid)
    idx = {v: np.where(vid == v)[0] for v in vids}
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        s = np.concatenate([idx[v] for v in rng.choice(vids, len(vids))])
        out.append(np.mean([b[s][cat[s] == c].mean() - a[s][cat[s] == c].mean() for c in CATS if (cat[s] == c).any()]))
    return float(np.quantile(out, .05)), float(np.quantile(out, .95))


def reference_cvq(val: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    key = dict(zip(zip(test.video_id, test.question.map(pp.norm_question)), test.qid))
    tq = [key.get((v, pp.norm_question(q))) for v, q in zip(val.video_id, val.question)]
    full = read(RUN / "test" / "cvq" / "geometry.csv", [t if t is not None else -1 for t in tq])
    low = read(RUN / "val" / "cvq" / "geometry.csv", val.qid)
    return np.where(np.isfinite(full), full, low)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="folder with val/ and test/ (outputs/trackb_ctx)")
    ap.add_argument("--lovo", action="store_true")
    a = ap.parse_args(argv)
    root = Path(a.root)
    val, test = questions("val"), questions("test")
    y, cat, vid = val.answer.to_numpy(float), val.category.to_numpy(), val.video_id.to_numpy()
    ref = reference_cvq(val, test)
    it_ref = items(ref, y)
    sd = val.tk.isin(["size", "distance"]).to_numpy()
    print(f"reference cvq_geo: macro {macro(it_ref, cat):.4f}, size/distance rows {it_ref[sd].mean():.4f} (n {sd.sum()})")
    facts = pd.read_csv(FACTS) if FACTS.exists() else None
    ref_t = read(RUN / "test" / "cvq" / "geometry.csv", facts.qid) if facts is not None else None
    rows, verdict = [], {}
    for name, rel in NEW.items():
        v = read(root / "val" / rel, val.qid)
        if not np.isfinite(v).any():
            continue
        it = items(v, y)
        d = macro(it, cat) - macro(it_ref, cat)
        lo, hi = boot(it_ref, it, cat, vid)
        d_sd = it[sd].mean() - it_ref[sd].mean()
        r = {"method": name, "MRA": macro(it, cat), **{c: it[cat == c].mean() for c in CATS}, "delta": d,
             "ci_lo": lo, "ci_hi": hi, "d_size_dist": d_sd, "cov": float(np.isfinite(v).mean())}
        if facts is not None:
            t = read(root / "test" / rel, facts.qid)
            ch = np.isfinite(t) & ~np.isclose(t, ref_t, rtol=1e-6, equal_nan=False)
            gain = items(t, facts.lab)[ch] - items(ref_t, facts.lab)[ch]
            r.update(fact_changed=int(ch.sum()), fact_gain=float(gain.mean()) if ch.any() else math.nan,
                     fact_cov=float(np.isfinite(t).mean()))
        ok = (d >= 0.03 and lo > 0, d_sd >= 0.05,
              r.get("fact_cov", 0.0) >= 0.90 and (r.get("fact_changed", 0) == 0 or r.get("fact_gain", 0) >= 0))
        r["criteria_1_3"] = "".join("Y" if x else "n" for x in ok)
        verdict[name] = all(ok) and name in PRIMARY
        rows.append(r)
    print(pd.DataFrame(rows).set_index("method").round(4).to_string())
    print("criteria 1-3 met by a pre-declared method:", [k for k, v in verdict.items() if v] or "none")
    if a.lovo:
        lovo(root, [k for k in NEW if (root / "val" / NEW[k]).exists() and (root / "test" / NEW[k]).exists()])


def lovo(root: Path, new: list[str]) -> None:
    """Criterion 4 with the research/trackb_v5 harness (validation rows inside the test table, family rules)."""
    sys.path.insert(0, str(ROOT / "research" / "trackb_v5"))
    from harness import V3, Data
    D = Data()
    for k in new:
        t = pd.read_csv(root / "test" / NEW[k]).set_index("id").parsed_value
        v = pd.read_csv(root / "val" / NEW[k]).set_index("id").parsed_value
        D.add_method(k, pd.to_numeric(t, errors="coerce"), pd.to_numeric(v, errors="coerce"))
    base = ["qwen_direct", "caw", "qwen_geo", "cv_geo", "cvq_geo"]
    pool = base + new
    I = {}
    for kk in range(1, 5):
        for ms in itertools.combinations(pool, kk):
            post, _ = D.rules(D.combined({c: list(ms) for c in CATS}))
            I["+".join(ms)] = D.items(post)
    I = pd.DataFrame(I)
    cat, vid = D.vcat, D.vvid

    def run(cols):
        held = pd.Series(np.nan, index=I.index)
        for c in CATS:
            mc = cat == c
            for v in vid[mc].unique():
                h, tr = mc & (vid == v), mc & (vid != v)
                held[h] = I.loc[h, I.loc[tr, cols].mean().idxmax()]
        return float(np.mean([held[cat == c].mean() for c in CATS]))

    old4 = [k for k in I.columns if all(m in base[:4] for m in k.split("+"))]
    old5 = [k for k in I.columns if all(m in base for m in k.split("+"))]
    lo_old4, lo_base, lo_new = run(old4), run(old5), run(list(I.columns))
    print(f"LOVO macro: v3's search (old 4) {lo_old4:.4f}; old 4 + cvq_geo {lo_base:.4f}; with new methods "
          f"{lo_new:.4f}; criterion 4 (new >= old4+cvq + 0.010) {'MET' if new and lo_new >= lo_base + 0.010 else 'not met'}")
    ins = {c: I.loc[cat == c].mean().idxmax() for c in CATS}
    print("in-sample best sets per category:", ins)


if __name__ == "__main__":
    main()
