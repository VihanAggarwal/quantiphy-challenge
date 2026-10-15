"""Build Track B candidate B1 (research/r86/PLAN.md section 2 item B1, section 3 step 1): one upload, read per category.

    .venv/bin/python research/trackb_v5/build_b1.py --out submissions/trackB_cand_B1.csv \
        [--keep S2,D2,S3,D3] [--rows research/trackb_v5/B1_rows.csv] [--decompose] [--val]

Track B inputs only: open-weight member outputs (/tmp/claude-0/tb3/x/trackb_v1, research/trackb_dense/out,
research/trackb_v5/out_test_cvq_seg.csv), model-free code (qp.postprocess, labnoise_open, path85b_phys) and the test
inputs (question / prior / depth text). The S2 routing table holds member NAMES only; it was selected at development
time with Track A pseudo-labels (research/r86/intel_tb_pseudolabel, FAQ: disclosed). No Track A answer value is read.

Components (each targets one category, so a leaderboard read per category isolates it):
  l2q     S3/D3: qwen_geo -> qwen_fov in the v3 member sets (v5 MAIN L2', fixed lab camera, Qwen member).
  s2route S2: per-cell log-median member set from routing_base8_min25_k2.csv (cell = category|source|unit kind),
          other S2 rows the S2 fallback set (fallback_category_sets.json); a routed row with no finite member value
          takes the S2 fallback set, then the v3 S2 set.
  l6s     D2 only: rows of simulation clips with a frame-aligned segmented twin -> the snapped cvq geometry where it is
          valid (v5plus L6s, build_v5.l6s_values), before the rules.
  (rules) qp.postprocess preset "trackb" on the whole test table (pool rule spill-over is accepted and logged).
  l1      S3: lab motion rows without a stated value x the lab label-noise emulator factor (v5 MAIN L1).
  l4      D2 only: free-fall speed rows of the simulation drop events -> a*(t_k - t0 - 1/(2 fps)) (v5plus L4).
  clamp   all categories: car width -> [1.5, 2.3] m, person height -> [1.50, 2.00] m (a-priori ranges; the regexes of
          research/r86/pp_strategy/guard_tb.py restricted to these two classes); questions or priors containing
          "toy" and rows whose value a stated-fact rule set are left alone. No car length / height, no balls / wheels.
Then --keep: categories not kept take the uploaded v3 values row by row (the per-category revert of the kill test).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "research" / "trackb_dense"))
from harness import CATS, V3, VAL_OFFSET, Data, fmt  # noqa: E402
import labnoise_open as LN  # noqa: E402
from build_v5 import STATED, l6s_values  # noqa: E402
from tbcommon import RUN, read_csv, specs as load_specs, with_fallback  # noqa: E402

PLD = ROOT / "research/r86/intel_tb_pseudolabel"
V3_FILE = ROOT / "submissions/trackB_v3_catmedian_famrules.csv"
COMPS = ("l2q", "s2route", "l6s", "l1", "l4", "clamp")
TARGET = {"l2q": ("S3", "D3"), "s2route": ("S2",), "l6s": ("D2",), "l1": ("S3",), "l4": ("D2",), "clamp": CATS}
TO_M = {"m": 1.0, "meters": 1.0, "meter": 1.0, "cm": 0.01, "mm": 0.001}
CLAMP = [("person height", r"\bheight of the (?:\w+ )?(?:person|man|woman|pedestrian)\b", 1.50, 2.00),
         ("car width", r"\bwidth of the (?:\w+ )?car\b", 1.5, 2.3)]


def unit_kind(u) -> str:
    """Cell unit kind of research/r86/intel_tb_pseudolabel/pseudo_tb.py (the routing table's definition)."""
    u = str(u).lower()
    return "A" if ("s^2" in u or "s2" in u or "s²" in u) else ("V" if "/s" in u or "per s" in u else "L")


def cells(frame: pd.DataFrame) -> pd.Series:
    return frame.category + "|" + frame.video_source.astype(str).str.split("_").str[0] + "|" + frame.target_unit.map(unit_kind)


def routing():
    R = pd.read_csv(PLD / "routing_base8_min25_k2.csv")
    cs = {r.cell: r.members.split("+") for r in R.itertuples() if r.cell.split("|")[0] == "S2"}
    fb = json.load(open(PLD / "fallback_category_sets.json"))["S2"]
    return cs, fb


def lmed(D, split, ms, mask):
    L = np.log(np.vstack([D.P[split][m].to_numpy(float) for m in ms]))
    L[~np.isfinite(L)] = np.nan
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return np.exp(np.nanmedian(L, 0))[mask]


def raw_split(D, split, comps, info):
    frame = D.test if split == "test" else D.val
    sets = {c: [("qwen_fov" if m == "qwen_geo" and c in ("S3", "D3") and "l2q" in comps else m) for m in v]
            for c, v in V3.items()}
    raw = D.raw(sets, split)
    if "s2route" in comps:
        cs, fb = routing()
        cell = cells(frame).to_numpy()
        s2 = (frame.category == "S2").to_numpy()
        val = np.full(len(frame), np.nan)
        val[s2] = lmed(D, split, fb, s2)
        nroute = {}
        for c, ms in cs.items():
            m = cell == c
            val[m] = lmed(D, split, ms, m)
            nroute[c] = int(m.sum())
        bad = s2 & ~(np.isfinite(val) & (val > 0))
        nfb = int(bad.sum())
        val[bad] = lmed(D, split, fb, bad)
        bad2 = s2 & ~(np.isfinite(val) & (val > 0))
        val[bad2] = raw.to_numpy()[bad2]
        raw = pd.Series(np.where(s2, val, raw.to_numpy()), index=raw.index)
        info[f"s2route_{split}"] = dict(routed_rows=nroute, nan_to_fallback=nfb, nan_to_v3=int(bad2.sum()))
    if "l6s" in comps:
        v = l6s_split(D, split)
        cat = frame.set_index("qid").category
        v = v[v.index.map(cat) == "D2"]
        raw.loc[v.index] = v.to_numpy()
        info[f"l6s_{split}"] = int(len(v))
    return raw


def l6s_split(D, split):
    if split == "test":
        return l6s_values(D)
    # same rule as build_v5.l6s_values on the validation clips (validation score only)
    R = pd.read_csv(HERE / "out_val_cvq_seg.csv")
    R = R[R.video_id.str.startswith("simulation")].set_index("id")
    sp = load_specs("val")
    kinds = pd.Series({q: sp[q].target.kind for q in R.index if q in sp})
    caw = pd.Series(D.P["val"]["caw"].to_numpy(), index=D.val.qid)
    v = with_fallback(R.geo_value, R.geo_si, kinds, caw.reindex(R.index)).dropna()
    return v[~np.isclose(v, caw.reindex(v.index), rtol=1e-9) & np.isclose(v, R.geo_value.reindex(v.index), rtol=1e-9)]


def clamp(frame: pd.DataFrame, pred: pd.Series, protected: set):
    f = frame.set_index("qid")
    q, u, p = f.question.str.lower(), f.target_unit.astype(str).str.lower().str.strip(), f.prior.astype(str).str.lower()
    out, hit = pred.copy(), {}
    notoy = ~q.str.contains("toy") & ~p.str.contains("toy")
    for nm, rx, lo, hi in CLAMP:
        msk = q.str.contains(rx, regex=True) & u.isin(list(TO_M)) & notoy & ~f.index.isin(list(protected))
        for i in f.index[msk]:
            if i not in out.index:
                continue
            k = TO_M[u[i]]
            v = float(out[i]) * k
            if np.isfinite(v) and v > 0 and not (lo <= v <= hi):
                out[i] = float(np.clip(v, lo, hi)) / k
                hit[i] = nm
    return out, hit


def build(D, comps, table="test"):
    """Final answers. table='test': the submission (test question table, as build_v5). table='combined': validation
    rows put into the test table (harness.Data.df), for scoring only."""
    comps, info = set(comps), {}
    rt = raw_split(D, "test", comps, info)
    if table == "test":
        raw, df = rt, D.test
    else:
        rv = raw_split(D, "val", comps, info)
        raw = pd.concat([rt.reindex(D.test.qid[~D.dup]), pd.Series(rv.to_numpy(), index=D.val.qid.to_numpy() + VAL_OFFSET)])
        df = D.df
    post, log = D.rules(raw, df=df)
    final = post.copy()
    stated = set(log[log.applied & log.rule.isin(STATED)].qid.astype(int))
    if "l1" in comps:
        cat = df.set_index("qid").category
        frames = []
        for split, off in (("test", 0), ("val", VAL_OFFSET)) if table == "combined" else (("test", 0),):
            A = pd.Series({q - off: v for q, v in post.items() if (q >= VAL_OFFSET) == (off > 0)})
            F = LN.factors(split, "qwen", A, 0.02, 0.02)
            F["qid"] = F.id + off
            frames.append(F)
        F = pd.concat(frames)
        F = F[F.qid.isin(cat.index) & (F.qid.map(cat) == "S3") & ~F.qid.isin(stated) & (F.factor != 1)]
        final.loc[F.qid] = final.loc[F.qid].to_numpy() * F.factor.to_numpy()
        info["l1"] = int((F.qid < VAL_OFFSET).sum())
    if "l4" in comps:
        C = pd.read_csv(ROOT / "research/path85b_phys/changes_ffbd.csv")
        cat = D.test.set_index("qid").category
        C = C[(C.qid.map(cat) == "D2") & C.qid.isin(final.index)]
        final.loc[C.qid] = C.new.to_numpy()
        info["l4"] = int(len(C))
    if "clamp" in comps:
        final, hit = clamp(df, final, stated)
        info["clamp"] = hit
    return raw, post, final, log, info


def keep_cats(D, final, keep):
    v3 = pd.read_csv(V3_FILE).set_index("id").parsed_value
    cat = D.test.set_index("qid").category
    rev = final.index[~final.index.map(cat).isin(keep)]
    out = final.copy()
    out.loc[rev] = v3.reindex(rev).to_numpy()
    return out


def changed(a: pd.Series, b: pd.Series) -> pd.Series:
    return pd.Series(~np.isclose(a.to_numpy(float), b.reindex(a.index).to_numpy(float), rtol=1e-9, equal_nan=True),
                     index=a.index)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--keep", default=",".join(CATS))
    ap.add_argument("--comps", default=",".join(COMPS))
    ap.add_argument("--rows", default="")
    ap.add_argument("--decompose", action="store_true")
    ap.add_argument("--val", action="store_true")
    a = ap.parse_args(argv)
    keep = [c for c in a.keep.split(",") if c]
    comps = [c for c in a.comps.split(",") if c]
    assert set(comps) <= set(COMPS), comps
    D = Data()
    D.add_method("cv_geo_only", read_csv(RUN / "test/cv/cv_geometry.csv", D.test.qid),
                 read_csv(RUN / "val/cv/cv_geometry.csv", D.val.qid))
    raw, post, final, log, info = build(D, comps)
    for k, v in info.items():
        print(k, v if k != "clamp" else f"{len(v)} rows {pd.Series(v).value_counts().to_dict()}")
    final = keep_cats(D, final, keep)
    assert final.notna().all() and np.isfinite(final).all() and (final > 0).all()
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        pd.DataFrame({"id": D.test.qid, "parsed_value": final.reindex(D.test.qid).to_numpy()}).to_csv(fh, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, a.out], check=True)
    print("wrote", a.out)

    t = D.test.set_index("qid")
    scored = pd.Series(~D.dup, index=D.test.qid)
    v3 = pd.read_csv(V3_FILE).set_index("id").parsed_value.reindex(t.index)
    out = pd.read_csv(a.out).set_index("id").parsed_value.reindex(t.index)

    def per_cat(mask):
        m = mask.reindex(t.index).fillna(False).astype(bool)
        return {c: f"{int((m & (t.category == c)).sum())}/{int((m & scored & (t.category == c)).sum())}" for c in CATS}

    print("B1 vs uploaded v3, rows changed per category (all/scored):", per_cat(changed(out, v3)))
    if not a.decompose:
        return
    rb0, pb0, b0, _, _ = build(D, [])
    assert not changed(b0, v3).any(), "base rebuild must reproduce the uploaded v3"
    print("base rebuild == uploaded v3: OK")
    rows = pd.DataFrame({"video_id": t.video_id, "category": t.category, "scored": scored.reindex(t.index),
                         "v3": v3, "b1": out})
    rows["changed"] = changed(out, v3)
    rows["raw_changed"] = changed(raw.reindex(t.index), rb0.reindex(t.index))
    att = {q: [] for q in t.index}
    print("\ncomponent | alone vs v3 (all/scored) | spill-over of the alone build (raw unchanged, final changed) | "
          "leave-one-out share of B1 (all/scored)")
    for k in comps:
        r1, p1, f1, _, _ = build(D, [k])
        ch1 = changed(f1, v3)
        spill = ch1 & ~changed(r1, rb0) if k in ("l2q", "s2route", "l6s") else ch1 & False
        spill_out = spill & ~t.category.isin(TARGET[k])
        rl, pl, fl, _, _ = build(D, [c for c in comps if c != k])
        fl = keep_cats(D, fl, keep)
        loo = changed(out, fl)
        for q in loo.index[loo]:
            att[q].append(k)
        rows[f"spill_{k}"] = spill
        print(f"{k:8s} | {per_cat(ch1)} | in-target {per_cat(spill & t.category.isin(TARGET[k]))} "
              f"other-cat {per_cat(spill_out)} | {per_cat(loo)}")
    rows["components"] = pd.Series({q: "+".join(v) for q, v in att.items()})
    if a.rows:
        rows[rows.changed | rows.filter(like="spill_").any(axis=1)].to_csv(a.rows)
        print("wrote", a.rows)
    if a.val:
        base_c = build(D, [], "combined")[2]
        print("\nvalidation (combined table; labels read only here, for scoring):")
        print("  v3     ", fmt(D.score(base_c)))
        for k in list(comps) + ["ALL"]:
            fc = build(D, comps if k == "ALL" else [k], "combined")[2]
            print(f"  {k:7s}", fmt(D.score(fc)), "| boot", fmt(D.boot(base_c, fc)))


if __name__ == "__main__":
    main()
