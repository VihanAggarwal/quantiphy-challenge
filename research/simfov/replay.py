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
Writes one row per (run, qid) with the direct answer, every variant, and the old solve's f / FOV / sensitivity.
"""
from __future__ import annotations

import argparse
import json
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

RUNS = ["test_v1_high_854", "test_3dnl_v1_high_b", "test_3dnl_v2_high"]
VARIANTS = {"geo_cam05": 0.05, "geo_cam15": 0.15, "geo_fix": 0.01}


def sim3d(df: pd.DataFrame) -> pd.DataFrame:
    return df[df.video_id.str.startswith("simulation") & df.category.isin(["S3", "D3"])]


def fov_map(fov_csv: str) -> dict[str, float]:
    """{video_id (originals and segmented twins): horizontal FOV in degrees}."""
    d = pd.read_csv(fov_csv)
    g = d.groupby("video_id").agg(h=("hfov_deg", "median"), v=("vfov_deg", "median"))
    out = {v: float(r.h) for v, r in g.iterrows()}
    tw = json.loads((ROOT / "runs/_postprocess_cache/twins_v3.json").read_text())
    for v, r in g.iterrows():
        s = tw.get(f"{v}|{v}_segmented", {})
        rot = s.get("status") == "rotated" and s.get("transform") in ("rot90", "rot270", "transpose", "anti_transpose")
        out[f"{v}_segmented"] = float(r.v if rot else r.h)
    return out


def replay(run: str, df: pd.DataFrame, fov: dict[str, float]) -> pd.DataFrame:
    records = rc.load_records(ROOT / "runs" / run / "test" / "records")
    records = {v: r for v, r in records.items() if v in set(df.video_id)}
    df = df[df.video_id.isin(records)]
    anns = rc.annotations(df, records, dense="motion", dense_cache=ROOT / "runs" / "_dense_cache" / "test",
                          dense_workers=2)
    recs = rc.prepare_records(df, records)
    rows = []
    for r in df.itertuples():
        a = anns.get(int(r.qid))
        if a is None:
            continue
        rec = recs[r.video_id]
        size, fps = tuple(rec["meta"]["image_size"]), float(rec["meta"]["fps"])
        seen = float(rec["meta"].get("scale") or 1.0)
        row = dict(run=run, qid=int(r.qid), video_id=r.video_id, category=r.category,
                   kind=a.spec.target.kind, prior_kind=a.spec.prior.kind if a.spec.prior else None,
                   direct=a.direct_answer, fov_model=fov.get(r.video_id, math.nan), W=size[0])
        ans = G.solve(a.spec, a.tracks, size, fps, seen_scale=seen)
        row.update(geo_old=ans.value, fov_old=ans.debug.get("fov_deg"), sens_old=ans.debug.get("f_sensitivity"),
                   method_old=ans.method, flags_old=";".join(ans.flags))
        f_cam = fov.get(r.video_id)
        for name, sig in VARIANTS.items():
            if not f_cam:
                row[name] = math.nan
                continue
            G.CAM_SIG_LOG_F = sig
            try:
                b = G.solve(a.spec, a.tracks, size, fps, seen_scale=seen, camera_fov_deg=f_cam)
            finally:
                G.CAM_SIG_LOG_F = 0.05
            row[name] = b.value
            if name == "geo_cam05":
                row.update(fov_cam05=b.debug.get("fov_deg"), flags_cam05=";".join(b.flags),
                           prior_meas_cam05=b.debug.get("prior_measured_si"),
                           prior_val=a.spec.prior.value_si if a.spec.prior else None)
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
