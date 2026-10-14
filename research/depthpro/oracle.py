"""Diagnostic upper bound (NOT a method; uses truths to build the focal): how good can geometry on Claude's tracks
get if a FOV estimator returned the best possible CLIP-LEVEL focal? For each size row with an exact fact or a
validation label whose geometry is ~ 1/f (stage1.primary_ref), the oracle focal is the log-median of f_ref over the
OTHER rows of the same clip (leave-one-row-out; all 3 runs of the held-out row excluded). Geometry at that focal:
geo = geo_fix * f_fix / f_oracle (exact for 1/f rows). Compared with dmed (3-run direct median) and with geometry at
the Depth Pro / MoGe focal on the same rows. Item MRA per row = qp.mra.item_scores on the 3-run log-median.

    .venv/bin/python research/depthpro/oracle.py research/depthpro/out/fov_depthpro.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from qp.mra import item_scores  # noqa: E402
import stage1 as s1  # noqa: E402


def main(fov_csv: str):
    replay = str(ROOT / "research/simfov/out/replay.csv")
    lab_f, lab_v, t = s1.truths(replay)
    truth = pd.concat([lab_f, lab_v[~lab_v.index.isin(lab_f.index)]])
    src = pd.concat([pd.Series("fact", index=lab_f.index), pd.Series("val", index=lab_v.index[~lab_v.index.isin(lab_f.index)])])
    r = pd.read_csv(replay)
    p = s1.primary_ref(r, truth, None)
    p["tf"] = 1 / np.tan(np.radians(p.fov_fix) / 2)
    p["f_fix_px"] = 0.5 * p.W * p.tf
    p["k"] = p.geo_fix * p.f_fix_px          # geo = k / f
    dp, mg = s1.model_fpx(fov_csv), s1.model_fpx(str(ROOT / "research/simfov/out/fov_moge.csv"))
    rows = []
    for q, g in p.groupby("qid"):
        c = g.cid.iloc[0]
        others = p[(p.cid == c) & (p.qid != q)]
        f_or = np.exp(np.log(others.f_px_ref).median()) if len(others) else np.nan
        k = np.exp(np.log(g.k).median())         # 3-run log-median of the 1/f constant
        rows.append(dict(qid=q, cid=c, src=src.get(q), truth=g.truth.iloc[0], dmed=t.dmed.get(q),
                         geo_oracle=k / f_or, geo_dp=k / dp.f_px.get(c, np.nan), geo_moge=k / mg.f_px.get(c, np.nan),
                         geo_old=t.old.get(q), n_other=others.qid.nunique()))
    d = pd.DataFrame(rows)
    d = d[d.n_other >= 1]
    cols = ["dmed", "geo_old", "geo_oracle", "geo_moge", "geo_dp"]
    for c in cols:
        d["s_" + c] = item_scores(d[c].fillna(d.dmed).to_numpy(), d.truth.to_numpy())
    d["s_gm_oracle"] = item_scores(np.sqrt(d.dmed * d.geo_oracle).to_numpy(), d.truth.to_numpy())
    has_dp = d.cid.isin(dp.index)
    print(f"size rows with a LOO clip focal: {len(d)} ({d.cid.nunique()} clips); with Depth Pro focal: {int(has_dp.sum())}")
    for name, m in (("all", slice(None)), ("facts", d.src == "fact"), ("val", d.src == "val"), ("with DP", has_dp)):
        x = d[m]
        print(f"  {name:8s} n={len(x):3d}  " + "  ".join(f"{c} {x['s_' + c].mean():.3f}" for c in cols + ["gm_oracle"]))
    rng = np.random.default_rng(0)
    clips = d.cid.unique()
    diff = (d.s_geo_oracle - d.s_dmed).groupby(d.cid).agg(["sum", "size"])
    bs = [diff.loc[rng.choice(clips, len(clips))].pipe(lambda z: z["sum"].sum() / z["size"].sum()) for _ in range(2000)]
    print(f"oracle-focal geometry - dmed: {d.s_geo_oracle.mean() - d.s_dmed.mean():+.3f} "
          f"(clip bootstrap 90% {np.percentile(bs, 5):+.3f} .. {np.percentile(bs, 95):+.3f})")
    print("median |log(pred/truth)|:", {c: round(float(np.median(np.abs(np.log(d[c] / d.truth)))), 3) for c in cols if d[c].notna().any()})
    d.to_csv(Path(fov_csv).with_name("oracle_rows.csv"), index=False)


if __name__ == "__main__":
    main(sys.argv[1])
