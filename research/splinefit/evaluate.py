"""Pre-registered evaluation (RESULT.md) of the spline derivative estimators on 2D geometry.

    .venv/bin/python research/splinefit/evaluate.py [--val out/val_hires_val_hr_v1_high.csv]
        [--test out/test_test_v1_high_854.csv] [--secondary out/val_val_opus_high.csv,...]

Sources: (1) validation labels of the val run's 2D questions; (2) stated-fact rows of test (qp.postprocess "facts",
speed guard off, conflicting statements skipped) replayed from the test run. Labels are read only here.
Routed answer = combo3's routing of the pipeline value (see routed()). Affected = |log(new/old)| > 0.005.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from qp import postprocess as pp  # noqa: E402
from qp.data import load_split  # noqa: E402
from qp.mra import item_scores  # noqa: E402

MOT = "acceler|veloc|speed|travel"
EPS = 0.005
N_SCORED = {"S2": 553, "D2": 1137}
VARIANTS = ("gcv", "h010", "h025", "gcv_glock")


def routed(r: pd.DataFrame, q: pd.DataFrame) -> pd.Series:
    """combo3's routing on 2D rows from one replay mode: S2 internet geometry -> direct (U1), S2 simulation(+seg)
    motion geometry -> sqrt(geo * direct) (U2), else run_claude.build_results' choice."""
    r = r.join(q[["question"]], on="id", rsuffix="_q")
    src = r.video_source.replace({"segmentation": "simulation"})
    geo = r.method.fillna("").str.startswith("geometry") & (r.geo_value > 0) & (r.direct_value > 0)
    mot = r.question.str.lower().str.contains(MOT)
    v = r.parsed_value.astype(float).copy()
    m1 = (r.category == "S2") & (src == "internet") & geo
    v[m1] = r.direct_value[m1]
    m2 = (r.category == "S2") & (src == "simulation") & mot & geo
    v[m2] = np.sqrt(r.geo_value[m2] * r.direct_value[m2])
    return pd.Series(v.to_numpy(), index=r.id.to_numpy())


def table(path: Path, q: pd.DataFrame) -> pd.DataFrame:
    r = pd.read_csv(path)
    out = {}
    for mode, g in r.groupby("mode"):
        out[mode] = routed(g.reset_index(drop=True), q)
    t = pd.DataFrame(out)
    first = r[r["mode"] == "base"].set_index("id")
    t["video_id"], t["category"], t["video_source"] = first.video_id, first.category, first.video_source
    t["geo_base"] = first.geo_value
    t["kind"] = np.where(q.question.reindex(t.index).str.lower().str.contains(MOT), "motion", "static")
    return t


def clip(v: pd.Series) -> pd.Series:
    return v.str.replace("_segmented", "", regex=False)


def boot(d: pd.DataFrame, n: int = 2000, seed: int = 0) -> tuple[float, float]:
    g = d.groupby("clipid").delta.agg(["sum", "size"])
    rng = np.random.default_rng(seed)
    k = rng.integers(0, len(g), (n, len(g)))
    s, c = g["sum"].to_numpy()[k].sum(1), g["size"].to_numpy()[k].sum(1)
    b = s / c
    return float(np.percentile(b, 5)), float(np.percentile(b, 95))


def score_rows(t: pd.DataFrame, labels: pd.Series, mode: str, source: str) -> pd.DataFrame:
    x = t.loc[t.index.intersection(labels.index)].copy()
    old, new = x["base"].astype(float), x[mode].astype(float)
    lr = np.log(new / old)
    x = x[np.abs(lr) > EPS]
    if x.empty:
        return pd.DataFrame(columns=["qid", "source", "category", "kind", "clipid", "old", "new", "label", "s_old",
                                     "s_new", "delta"])
    lab = labels.reindex(x.index).astype(float)
    so, sn = item_scores(x["base"].to_numpy(float), lab.to_numpy()), item_scores(x[mode].to_numpy(float), lab.to_numpy())
    return pd.DataFrame({"qid": x.index, "source": source, "category": x.category.to_numpy(), "kind": x.kind.to_numpy(),
                         "clipid": clip(x.video_id).to_numpy(), "video_id": x.video_id.to_numpy(),
                         "old": x["base"].to_numpy(), "new": x[mode].to_numpy(), "label": lab.to_numpy(),
                         "s_old": so, "s_new": sn, "delta": sn - so})


def summarize(d: pd.DataFrame, label: str) -> dict:
    if d.empty:
        print(f"  {label}: no affected rows")
        return dict(n=0, mean=0.0, lo=0.0, hi=0.0)
    lo, hi = boot(d)
    m = float(d.delta.mean())
    print(f"  {label}: n={len(d)} clips={d.clipid.nunique()} old {d.s_old.mean():.3f} new {d.s_new.mean():.3f} "
          f"delta {m:+.4f} (90% clip CI {lo:+.4f} .. {hi:+.4f}); item sum {d.delta.sum():+.2f}; "
          f"better {int((d.delta > 0).sum())} worse {int((d.delta < 0).sum())}")
    return dict(n=len(d), mean=m, lo=lo, hi=hi)


def test_changes(tt: pd.DataFrame, combo3: pd.Series, mode: str) -> dict:
    """combo3 rows that still hold the routed base value and whose routed value changes by > EPS."""
    base = tt["base"].astype(float)
    same = np.isclose(combo3.reindex(tt.index), base, rtol=1e-6)
    lr = np.log(tt[mode].astype(float) / base)
    ch = same & (np.abs(lr) > EPS) & np.isfinite(lr)
    return {c: int((ch & (tt.category == c)).sum()) for c in ("S2", "D2")} | {"_mask": ch}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--val", default=str(HERE / "out/val_hires_val_hr_v1_high.csv"))
    ap.add_argument("--test", default=str(HERE / "out/test_test_v1_high_854.csv"))
    ap.add_argument("--secondary", default="")
    ap.add_argument("--dump", default=str(HERE / "out/eval_rows.csv"))
    a = ap.parse_args()
    test = load_split("test").set_index("qid")
    val = load_split("val_hires").set_index("qid")
    tv = table(Path(a.val), val)
    tt = table(Path(a.test), test)
    lab_v = val.answer.astype(float)
    # stated facts on test, scored without the rule; a fact row identical to a validation question counts once (val)
    _, log = pp.apply_rules(tt["base"].reindex(test.index).fillna(1.0), test.reset_index(), rules=("facts",),
                            speed_guard=0)
    f = log[log.applied]
    lab_f = pd.Series(f.new.to_numpy(float), index=f.qid.astype(int))
    vkey = set(zip(val.video_id, val.question.map(pp.norm_question)))
    dup = [q for q in lab_f.index if (test.video_id[q], pp.norm_question(test.question[q])) in vkey]
    lab_f = lab_f.drop(dup)
    lab_f = lab_f[lab_f.index.isin(tt.index)]
    print(f"stated facts on 2D test rows: {len(lab_f)} (dropped {len(dup)} also in validation); "
          f"by category {test.category.reindex(lab_f.index).value_counts().to_dict()}")
    combo3 = pd.read_csv(ROOT / "submissions/trackA_combo3_on_combo2.csv").set_index("id").parsed_value.astype(float)
    rows, verdicts = [], {}
    for mode in VARIANTS:
        print(f"\n===== {mode} =====")
        dv = score_rows(tv, lab_v, mode, "val")
        df_ = score_rows(tt, lab_f, mode, "facts")
        d = pd.concat([dv, df_], ignore_index=True)
        d["mode"] = mode
        rows.append(d)
        sv = summarize(dv, "validation")
        sf = summarize(df_, "facts     ")
        sp = summarize(d, "POOLED    ")
        cat = {}
        for c in ("S2", "D2"):
            cat[c] = summarize(d[d.category == c], f"pooled {c} ")
            cat[c]["sum"] = float(d.delta[d.category == c].sum())
        for k in ("motion", "static"):
            summarize(d[d.kind == k], f"pooled target {k}")
        tc = test_changes(tt, combo3, mode)
        gain = sum(tc[c] * (cat[c]["mean"] if cat[c]["n"] else 0.0) / (4 * N_SCORED[c]) for c in ("S2", "D2"))
        print(f"  combo3 rows changed > {EPS}: S2 {tc['S2']} D2 {tc['D2']}; expected overall gain {gain:+.5f}")
        crit = {"a_mean>=.01": sp["mean"] >= 0.010, "b_ci_lo>0": sp["lo"] > 0,
                "c_no_cat_loss": all(cat[c]["sum"] >= 0 for c in ("S2", "D2")),
                "d_gain>=.002": gain >= 0.002, "e_sources>=0": sv["mean"] >= 0 and sf["mean"] >= 0}
        verdicts[mode] = crit
        print("  criteria:", crit, "->", "PASS" if all(crit.values()) else "FAIL")
    pd.concat(rows, ignore_index=True).to_csv(a.dump, index=False)
    for p in [s for s in a.secondary.split(",") if s]:
        split = "val_hires" if Path(p).name.startswith("val_hires") else "val"
        vq = load_split(split).set_index("qid")
        ts = table(Path(p), vq)
        print(f"\n--- secondary {Path(p).name} ---")
        for mode in VARIANTS:
            summarize(score_rows(ts, vq.answer.astype(float), mode, "val2"), mode)
    print("\nVERDICTS:", {m: ("PASS" if all(c.values()) else "FAIL") for m, c in verdicts.items()})


if __name__ == "__main__":
    main()
