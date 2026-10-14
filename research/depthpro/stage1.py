"""Stage 1 of the pre-registered kill test (RESULT.md): focal accuracy of a model FOV file against focal lengths
implied by exact stated facts / validation labels (primary) and by the stated size prior (secondary, as
research/simfov/fov_check.py (ii)). Truth values are read only to build the per-clip REFERENCE focal; nothing is
written to any answer.

    .venv/bin/python research/depthpro/stage1.py research/depthpro/out/fov_depthpro.csv \
        [--moge research/simfov/out/fov_moge.csv] [--replay research/simfov/out/replay.csv]

Primary reference, per (run, size-target row with a truth): the simfov replay ran geometry with f fixed to MoGe's
focal (geo_fix, fov_fix). For a size target whose geometry is ~ 1/f, the focal that reproduces the truth is
f_ref = f_fix * geo_fix / truth. Proportionality is checked in the same run against the old solve (f from the prior):
|log(geo_old * f_old / (geo_fix * f_fix))| < 0.02. Focal lengths are compared in pixels of the clip's original frame
(a rotated segmented twin's f_px equals its original's).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "research" / "simfov"))
from qp import postprocess as pp  # noqa: E402
from qp.data import load_split, load_validation  # noqa: E402
import evaluate as ev  # noqa: E402  (research/simfov/evaluate.py: table())

orig = lambda v: v.replace("_segmented", "")  # noqa: E731


def model_fpx(fov_csv: str) -> pd.DataFrame:
    d = pd.read_csv(fov_csv)
    g = d.groupby("video_id").agg(hfov=("hfov_deg", "median"), W=("W", "first"), H=("H", "first"),
                                  n=("hfov_deg", "size"))
    g["f_px"] = 0.5 * g.W / np.tan(np.radians(g.hfov) / 2)
    return g


def truths(replay_csv: str) -> tuple[pd.Series, pd.Series, pd.DataFrame]:
    t = ev.table(replay_csv)
    test = load_split("test")
    val = load_validation()
    key = lambda d: list(zip(d.video_id, d.question.map(pp.norm_question)))  # noqa: E731
    vmap = dict(zip(key(val), val.answer))
    lab_v = pd.Series([vmap.get(k, np.nan) for k in key(test)], index=test.qid).dropna()
    lab_v = lab_v[lab_v.index.isin(t.index)]
    _, log = pp.apply_rules(t.dmed.reindex(test.qid).fillna(1.0), test, rules=("facts",), speed_guard=0)
    f = log[log.applied]
    lab_f = pd.Series(f.new.to_numpy(float), index=f.qid.astype(int))
    lab_f = lab_f[lab_f.index.isin(t.index)]
    return lab_f, lab_v, t


def primary_ref(r: pd.DataFrame, truth: pd.Series, W0: pd.Series) -> pd.DataFrame:
    x = r[(r.kind == "size") & r.qid.isin(truth.index)].copy()
    x["truth"] = truth.reindex(x.qid).to_numpy()
    tf = 1 / np.tan(np.radians(x.fov_fix) / 2)        # f / (W/2) of the question's frame
    to = 1 / np.tan(np.radians(x.fov_old) / 2)
    x["prop"] = np.log(x.geo_old * to / (x.geo_fix * tf))
    x = x[np.isfinite(x.prop) & (x.prop.abs() < 0.02) & (x.geo_fix > 0)]
    x["f_px_ref"] = 0.5 * x.W * tf * x.geo_fix / x.truth   # f in pixels of the question's frame = original's
    x["cid"] = x.video_id.map(orig)
    return x


def secondary_ref(r: pd.DataFrame) -> pd.Series:
    x = r[(r.prior_kind == "size") & (r.method_old == "3d_focal_from_prior") & (r.sens_old >= 0.3)
          & ~r.video_id.str.endswith("_segmented")]
    fov = x.groupby("video_id").fov_old.median()
    W = x.groupby("video_id").W.first()
    return 0.5 * W / np.tan(np.radians(fov) / 2)


def score(name: str, fm: pd.DataFrame, ref: pd.Series) -> pd.Series:
    j = ref.index.intersection(fm.index)
    e = np.log(fm.f_px.reindex(j) / ref.reindex(j))
    print(f"  {name:8s} n={len(e):2d}  median log(f_model/f_ref) {e.median():+.3f}  median |e| {e.abs().median():.3f}  "
          f"share |e|<=.10 {(e.abs() <= .10).mean():.2f}  <=.20 {(e.abs() <= .20).mean():.2f}")
    return e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fov")
    ap.add_argument("--moge", default=str(ROOT / "research/simfov/out/fov_moge.csv"))
    ap.add_argument("--replay", default=str(ROOT / "research/simfov/out/replay.csv"))
    a = ap.parse_args()
    dp, mg = model_fpx(a.fov), model_fpx(a.moge)
    lab_f, lab_v, _ = truths(a.replay)
    truth = pd.concat([lab_f, lab_v[~lab_v.index.isin(lab_f.index)]])
    r = pd.read_csv(a.replay)
    p = primary_ref(r, truth, dp.W)
    # noise of the primary reference: spread of f_ref across the 3 runs of one row, and across rows of one clip
    sd_run = p.groupby("qid").f_px_ref.agg(lambda s: np.log(s).std() if len(s) > 1 else np.nan).median()
    sd_row = p.groupby(["cid", "qid"]).f_px_ref.median().groupby("cid").agg(
        lambda s: np.log(s).std() if len(s) > 1 else np.nan).median()
    prim = np.exp(np.log(p.f_px_ref).groupby(p.cid).median())
    sec = secondary_ref(r)
    print(f"primary reference: {len(p)} (run,row) pairs, {p.qid.nunique()} rows, {len(prim)} clips; "
          f"sd(log f_ref) across runs (median) {sd_run:.3f}, across rows within a clip {sd_row:.3f}")
    print(f"secondary (prior-implied, fov_check ii): {len(sec)} clips")
    cs = prim.index.intersection(sec.index)
    dis = np.log(prim.reindex(cs) / sec.reindex(cs))
    print(f"reference disagreement primary vs secondary on {len(cs)} common clips: median |log| {dis.abs().median():.3f} "
          f"(median signed {dis.median():+.3f})")
    print(f"Depth Pro FOV for {len(dp)} clips ({int(dp.n.sum())} frames)")
    print("\nPRIMARY reference (fact/val-implied):")
    e_dp = score("DepthPro", dp, prim)
    e_mg = score("MoGe-2", mg, prim.reindex(e_dp.index))
    print("SECONDARY reference (prior-implied):")
    s_dp = score("DepthPro", dp, sec)
    score("MoGe-2", mg, sec.reindex(s_dp.index))
    allref = np.exp(pd.concat([np.log(p.groupby("cid").f_px_ref.apply(list).explode().astype(float)),
                               np.log(sec)]).groupby(level=0).median())
    print("POOLED (primary rows + secondary) per clip:")
    score("DepthPro", dp, allref)
    score("MoGe-2", mg, allref.reindex(dp.index.intersection(allref.index)))
    tab = pd.DataFrame({"hfov_dp": dp.hfov, "hfov_moge": mg.hfov.reindex(dp.index), "f_dp": dp.f_px,
                        "f_moge": mg.f_px.reindex(dp.index), "f_ref_primary": prim.reindex(dp.index),
                        "f_ref_prior": sec.reindex(dp.index), "n_frames_dp": dp.n})
    tab["e_dp"] = np.log(tab.f_dp / tab.f_ref_primary)
    tab["e_moge"] = np.log(tab.f_moge / tab.f_ref_primary)
    tab["hfov_ref"] = np.degrees(2 * np.arctan(0.5 * dp.W / tab.f_ref_primary))
    print("\nper clip:")
    print(tab.round(3).to_string())
    n = len(e_dp)
    med, share = e_dp.abs().median(), (e_dp.abs() <= .10).mean()
    if n < 8:
        print(f"\nfewer than 8 primary clips ({n}): the bar uses the POOLED reference (pre-registered)")
    print(f"\nSTAGE 1 bar (primary): median |e| {med:.3f} <= .10 and share {share:.2f} >= .60 -> "
          f"{'PASS' if (med <= .10 and share >= .60) else 'FAIL'}")
    tab.to_csv(Path(a.fov).with_name("stage1_per_clip.csv"))


if __name__ == "__main__":
    main()
