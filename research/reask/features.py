"""Per-question risk features from a cached Claude run (records + run csv). No API calls.

Features (all label-free, computable on test and validation alike):
  kind       target kind from the parsed spec (size, speed, acceleration, distance, ...)
  motion     target is speed/acceleration/path-like (else static)
  conf       Claude's self-reported confidence (0..1)
  gd         |log(geo / direct)| when both exist
  t_q        target time asked (s) or nan
  t_end      clip duration (n_frames_total - 1) / fps
  beyond     t_q > t_end + 1 frame
  cov_gap    for timed targets: |t_q - nearest observed frame of the target track| in s (nan if untimed)
  n_obs      observations on the target track(s)
  prior_ratio  answer / prior value (both SI) when target and prior are the same kind
  dim        target dimension word ('' if none)
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MOTION = {"speed", "acceleration", "path_length", "displacement"}
UNIT_SI = {"m": 1, "cm": .01, "mm": .001, "km": 1000, "m/s": 1, "cm/s": .01, "km/h": 1 / 3.6, "mm/s": .001,
           "m/s^2": 1, "cm/s^2": .01, "mm/s^2": .001}


def run_table(run_dir: str, split: str) -> pd.DataFrame:
    rd = ROOT / run_dir
    csv = pd.read_csv(rd / f"{split}.csv").rename(columns={"id": "qid"}).set_index("qid")
    rows = []
    for f in sorted((rd / split / "records").glob("*.json")):
        d = json.load(open(f))
        meta = d.get("meta") or {}
        fps = float(meta.get("fps") or 0) or np.nan
        nft = meta.get("n_frames_total") or np.nan
        t_end = (nft - 1) / fps if fps == fps else np.nan
        for q in (d.get("parsed") or {}).get("questions", []):
            sp = q.get("spec") or {}
            tg, pr = sp.get("target") or {}, sp.get("prior") or {}
            kind = tg.get("kind", "")
            tq = tg.get("time")
            tq = float(tq) if isinstance(tq, (int, float)) else np.nan
            tgt_obs = [o["frame"] for tr in q.get("tracks") or [] if tr.get("role") == "target"
                       for o in tr.get("obs") or [] if isinstance(o.get("frame"), (int, float))]
            cov = np.nan
            if tq == tq and tgt_obs and fps == fps:
                cov = float(np.min(np.abs(np.array(tgt_obs) / fps - tq)))
            pv = pr.get("value_si")
            rows.append(dict(qid=int(q["qid"]), video_id=meta.get("video_id", f.stem), kind=kind,
                             pkind=pr.get("kind", ""), motion=kind in MOTION, conf=q.get("confidence"),
                             t_q=tq, t_end=t_end, n_obs=len(tgt_obs), cov_gap=cov,
                             prior_si=float(pv) if isinstance(pv, (int, float)) else np.nan,
                             dim=tg.get("dimension") or "", unit=tg.get("unit") or "",
                             n_tracks=len(q.get("tracks") or [])))
    ft = pd.DataFrame(rows).set_index("qid")
    ft = ft.join(csv[["parsed_value", "geo_value", "direct_value", "method"]], how="left")
    ft["conf"] = pd.to_numeric(ft["conf"], errors="coerce")
    with np.errstate(divide="ignore", invalid="ignore"):
        ft["gd"] = np.abs(np.log(ft.geo_value / ft.direct_value))
    ft["beyond"] = ft.t_q > ft.t_end + 0.05
    return ft


def add_prior_ratio(ft: pd.DataFrame, target_unit: pd.Series) -> pd.DataFrame:
    """answer (SI) / prior (SI) when the target and the prior are the same kind of quantity."""
    u = target_unit.reindex(ft.index).fillna("")
    si = ft.parsed_value * u.map(lambda x: UNIT_SI.get(x, np.nan))
    same = ((ft.kind == ft.pkind) | (ft.kind.isin(["size", "distance", "displacement", "path_length"])
                                    & ft.pkind.isin(["size", "distance", "displacement", "path_length"])))
    ft["prior_ratio"] = np.where(same, si / ft.prior_si, np.nan)
    return ft
