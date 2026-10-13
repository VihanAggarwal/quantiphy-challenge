"""Free replay of cached Claude runs on the 3D simulation clips (S3/D3, simulation_X and simulation_X_segmented)
with qp.geometry, f solved from the prior (old) vs f anchored on a model's FOV estimate (new). No API calls.

    ANTHROPIC_API_KEY="" ANTHROPIC_BASE_URL="http://127.0.0.1:9" QP_LEDGER=<scratch> \
        .venv/bin/python research/simfov/replay.py --fov research/simfov/out/fov_moge.csv --out research/simfov/out/replay.csv

Annotations: run_claude defaults (qp.refine of motion priors + dense motion tracks, cached in runs/_dense_cache/test).
The model FOV of a clip is the median over its frames; a segmented twin uses its original's FOV (the twin is a
pixel-aligned re-render), or the original's vertical FOV when qp.postprocess's twin check says the twin is the
original rotated by 90 degrees (simulation_0017 / _0019). Variants (CAM_SIG_LOG_F = sd of log f around the camera):
  geo_old     no camera (f solved from the prior; the pipeline's 3D non-lab geometry)
  geo_cam05   camera_fov_deg = model FOV, CAM_SIG_LOG_F 0.05 (qp.geometry default for a known camera)
  geo_cam15   same, CAM_SIG_LOG_F 0.15 (model FOV treated as ~15% uncertain)
  geo_fix     same, CAM_SIG_LOG_F 0.01 (model FOV taken as exact)
  geo_snap05  as geo_cam05 with the model focal snapped to a stock Blender lens (SNAP_TOL)
  geo_camZ05  as geo_cam05 with depth_info read as optical-axis Z instead of range (DEPTH_IS_RANGE False)
Writes one row per (run, qid) with the direct answer, every variant, and the old solve's f / FOV / sensitivity.
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import qp.geometry as G  # noqa: E402
import run_claude as rc  # noqa: E402
from qp.data import load_split  # noqa: E402

ANNS_CACHE = os.environ.get("SIMFOV_ANNS_CACHE", "")   # folder for pickled post-processed annotations (optional)
RUNS = ["test_v1_high_854", "test_3dnl_v1_high_b", "test_3dnl_v2_high"]
VARIANTS = {"geo_cam05": ("raw", 0.05, True), "geo_cam15": ("raw", 0.15, True), "geo_fix": ("raw", 0.01, True),
            "geo_snap05": ("snap", 0.05, True), "geo_camZ05": ("raw", 0.05, False)}   # (FOV map, CAM_SIG_LOG_F, DEPTH_IS_RANGE)


def sim3d(df: pd.DataFrame) -> pd.DataFrame:
    return df[df.video_id.str.startswith("simulation") & df.category.isin(["S3", "D3"])]


LENSES = np.array([14, 18, 20, 24, 28, 35, 50, 85, 100, 135, 200, 250], float)   # stock Blender lenses (mm)
SNAP_TOL = 0.10    # snap the model focal to a stock lens when within this log distance (fixed a priori)


def fov_map(fov_csv: str) -> dict[str, dict[str, float]]:
    """{"raw" | "snap": {video_id (originals and segmented twins): horizontal FOV in degrees}}. "snap": the model
    focal in mm (36 mm sensor on the larger image side, Blender sensor fit AUTO) moved to the nearest stock lens
    when within SNAP_TOL (log), else kept."""
    d = pd.read_csv(fov_csv)
    g = d.groupby("video_id").agg(h=("hfov_deg", "median"), W=("W", "first"), H=("H", "first"))
    tw = json.loads((ROOT / "runs/_postprocess_cache/twins_v3.json").read_text())
    out = {"raw": {}, "snap": {}}
    for v, r in g.iterrows():
        f_px = r.W / 2 / math.tan(math.radians(r.h) / 2)
        F = 36 * f_px / max(r.W, r.H)
        i = int(np.abs(np.log(F / LENSES)).argmin())
        f_snap = f_px * (LENSES[i] / F) if abs(math.log(F / LENSES[i])) <= SNAP_TOL else f_px
        s = tw.get(f"{v}|{v}_segmented", {})
        rot = s.get("status") == "rotated" and s.get("transform") in ("rot90", "rot270", "transpose", "anti_transpose")
        for key, f in (("raw", f_px), ("snap", f_snap)):
            out[key][v] = math.degrees(2 * math.atan(r.W / 2 / f))
            out[key][f"{v}_segmented"] = math.degrees(2 * math.atan((r.H if rot else r.W) / 2 / f))
    return out


def replay(run: str, df: pd.DataFrame, fov: dict[str, float]) -> pd.DataFrame:
    records = rc.load_records(ROOT / "runs" / run / "test" / "records")
    records = {v: r for v, r in records.items() if v in set(df.video_id)}
    df = df[df.video_id.isin(records)]
    pk = Path(ANNS_CACHE) / f"anns_{run}.pkl" if ANNS_CACHE else None
    if pk and pk.exists():
        anns = pickle.loads(pk.read_bytes())
    else:
        if os.environ.get("SIMFOV_FAST"):   # Claude's own tracks: no optical-flow refinement, no dense tracking
            anns = rc.annotations(df, records, refine_priors=False, dense="off")
        else:
            anns = rc.annotations(df, records, dense="motion", dense_cache=ROOT / "runs" / "_dense_cache" / "test",
                                  dense_workers=2)
        if pk:
            pk.parent.mkdir(parents=True, exist_ok=True)
            pk.write_bytes(pickle.dumps(anns))
    recs = rc.prepare_records(df, records)
    rows = []
    for i, r in enumerate(df.itertuples()):
        if i % 25 == 0:
            print(f"{run}: {i}/{len(df)}", flush=True)
        a = anns.get(int(r.qid))
        if a is None:
            continue
        rec = recs[r.video_id]
        size, fps = tuple(rec["meta"]["image_size"]), float(rec["meta"]["fps"])
        seen = float(rec["meta"].get("scale") or 1.0)
        row = dict(run=run, qid=int(r.qid), video_id=r.video_id, category=r.category,
                   kind=a.spec.target.kind, prior_kind=a.spec.prior.kind if a.spec.prior else None,
                   direct=a.direct_answer, fov_model=fov["raw"].get(r.video_id, math.nan), W=size[0])
        ans = G.solve(a.spec, a.tracks, size, fps, seen_scale=seen)
        row.update(geo_old=ans.value, fov_old=ans.debug.get("fov_deg"), sens_old=ans.debug.get("f_sensitivity"),
                   method_old=ans.method, flags_old=";".join(ans.flags))
        for name, (mkey, sig, rng) in VARIANTS.items():
            f_cam = fov[mkey].get(r.video_id)
            if not f_cam:
                row[name] = math.nan
                continue
            G.CAM_SIG_LOG_F, G.DEPTH_IS_RANGE = sig, rng
            try:
                b = G.solve(a.spec, a.tracks, size, fps, seen_scale=seen, camera_fov_deg=f_cam)
            finally:
                G.CAM_SIG_LOG_F, G.DEPTH_IS_RANGE = 0.05, True
            row[name] = b.value
            if name == "geo_cam05":
                row.update(fov_cam05=b.debug.get("fov_deg"), flags_cam05=";".join(b.flags),
                           prior_meas_cam05=b.debug.get("prior_measured_si"),
                           prior_val=a.spec.prior.value_si if a.spec.prior else None)
            if name == "geo_fix":
                row.update(fov_fix=b.debug.get("fov_deg"), target_si_fix=b.debug.get("value_si"))
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fov", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--runs", default=",".join(RUNS))
    a = ap.parse_args()
    df = sim3d(load_split("test"))
    fov = fov_map(a.fov)
    out = pd.concat([replay(run, df, fov) for run in a.runs.split(",")], ignore_index=True)
    out.to_csv(a.out, index=False)
    print(f"wrote {a.out}: {len(out)} rows; model FOV for {out.fov_model.notna().sum()}")


if __name__ == "__main__":
    main()
