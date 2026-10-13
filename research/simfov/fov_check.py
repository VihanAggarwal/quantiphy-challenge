"""Label-free sanity checks of the model FOV on the 3D simulation clips (test inputs only).

    .venv/bin/python research/simfov/fov_check.py research/simfov/out/fov_moge.csv research/simfov/out/replay.csv

(i)  same-camera clips: originals whose first / middle / last thumbnails are near-identical (NCC >= 0.97 on every
     aligned frame: same view, same lens) should get the same FOV; reports |log ratio| of their model FOVs.
     Frame stability: clips with several frames in the FOV file -> spread of hfov across frames.
(ii) prior-implied FOV: where the prior is a SIZE whose object has a depth_info entry and the old solve's f is well
     conditioned (method 3d_focal_from_prior, f-sensitivity >= 0.3), the FOV the old solver needed to reproduce the
     stated prior from Claude's track (prior_px * range / size) vs the model FOV: median |log ratio| of focal lengths.
(iii) Blender lens check: F_mm = 36 * f_px / max(W, H) (sensor fit AUTO, 36 mm sensor on the larger side); how many
     model / prior-implied focal lengths fall within +-5% of a stock lens {14,18,20,24,28,35,50,85,100,135,200,250}.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
LENSES = np.array([14, 18, 20, 24, 28, 35, 50, 85, 100, 135, 200, 250], float)


def f_mm(hfov_deg, W, H):
    f_px = W / 2 / np.tan(np.radians(np.asarray(hfov_deg, float)) / 2)
    return 36 * f_px / np.maximum(W, H)


def snap_err(F):
    F = np.asarray(F, float)
    i = np.abs(np.log(F[:, None] / LENSES[None])).argmin(1)
    return LENSES[i], np.log(F / LENSES[i])


def main(fov_csv, replay_csv):
    d = pd.read_csv(fov_csv)
    per = d.groupby("video_id").agg(hfov=("hfov_deg", "median"), W=("W", "first"), H=("H", "first"),
                                    n=("hfov_deg", "size"), sd=("hfov_deg", lambda s: np.log(s).std() if len(s) > 1 else np.nan))
    per["F_mm"] = f_mm(per.hfov, per.W, per.H)
    print(f"model FOV for {len(per)} clips; hfov quantiles:", per.hfov.quantile([0, .1, .25, .5, .75, .9, 1]).round(1).to_dict())
    print("hfov bins:", pd.cut(per.hfov, [0, 20, 60, 180]).value_counts().sort_index().to_dict())
    multi = per[per.n > 1]
    if len(multi):
        print(f"frame stability ({len(multi)} clips with >1 frame): sd of log hfov median {multi.sd.median():.3f}, "
              f"max {multi.sd.max():.3f}")
        print(d[d.video_id.isin(multi.index)].pivot_table(index="video_id", columns="frac", values="hfov_deg").round(1).to_string())
    # (i) same view by thumbnails
    z = np.load(ROOT / "runs/_postprocess_cache/thumbs_v3.npz", allow_pickle=False)
    th = {str(v): t.reshape(len(t), -1).astype(np.float32) for v, t in zip(z["ids"], z["th"])}
    ids = [v for v in per.index if v in th]
    U = {v: (th[v] - th[v].mean(1, keepdims=True)) / (th[v].std(1, keepdims=True) * th[v].shape[1] ** .5 + 1e-6) for v in ids}
    pairs = []
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            if U[a].shape != U[b].shape:
                continue
            ncc = float(min((U[a][k] @ U[b][k]) for k in range(len(U[a]))))
            if ncc >= 0.97:
                pairs.append((a, b, ncc, per.hfov[a], per.hfov[b]))
    if pairs:
        P = pd.DataFrame(pairs, columns=["a", "b", "ncc", "hfov_a", "hfov_b"])
        P["abslog"] = np.abs(np.log(np.tan(np.radians(P.hfov_a) / 2) / np.tan(np.radians(P.hfov_b) / 2)))
        print(f"\n(i) same-view pairs (thumbnail NCC >= .97): {len(P)}; median |log f ratio| {P.abslog.median():.3f}, "
              f"max {P.abslog.max():.3f}")
        print(P.round(3).to_string(index=False))
    # (ii) prior-implied FOV
    r = pd.read_csv(replay_csv)
    r = r[(r.prior_kind == "size") & (r.method_old == "3d_focal_from_prior") & (r.sens_old >= 0.3)
          & ~r.video_id.str.endswith("_segmented")]
    imp = r.groupby("video_id").fov_old.median()
    x = per.join(imp.rename("fov_prior"), how="inner")
    x["logr"] = np.log(np.tan(np.radians(x.hfov) / 2) / np.tan(np.radians(x.fov_prior) / 2))  # log(f_prior / f_model)
    print(f"\n(ii) size-prior clips with depth and well-conditioned f: {len(x)}; log(f_prior/f_model) median "
          f"{x.logr.median():+.3f}, median |.| {x.logr.abs().median():.3f}, share |.|<0.1: {(x.logr.abs() < .1).mean():.2f}, "
          f"<0.2: {(x.logr.abs() < .2).mean():.2f}")
    x["bin"] = pd.cut(x.hfov, [0, 20, 60, 180])
    print(x.groupby("bin", observed=True).logr.agg(["size", "median", lambda s: s.abs().median()]).round(3).to_string())
    print(x[["hfov", "fov_prior", "logr"]].round(2).sort_values("hfov").to_string())
    # (iii) lenses
    for name, F in (("model", per.F_mm.to_numpy()), ("prior-implied", f_mm(x.fov_prior, x.W, x.H).to_numpy())):
        L, e = snap_err(F)
        print(f"\n(iii) {name}: {len(F)} focal lengths; within 5% of a stock lens: {(np.abs(e) < .05).mean():.2f} "
              f"(uniform-in-log expectation ~{min(1, 2 * .05 * len(LENSES) / np.log(250 / 14)):.2f})")
        print("   histogram of F_mm:", np.histogram(F, bins=[0, 16, 19, 22, 26, 31, 40, 60, 90, 115, 160, 220, 400])[0].tolist(),
              "bins [<16,16-19,19-22,22-26,26-31,31-40,40-60,60-90,90-115,115-160,160-220,>220]")
    per.to_csv(Path(fov_csv).with_name("fov_per_clip.csv"))


if __name__ == "__main__":
    main(*sys.argv[1:3])
