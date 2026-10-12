"""Shared helpers for the lab distance study (research/labdist)."""
import json, glob, re, sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
BASE = ROOT / "submissions/trackA_probe8_p7b_d2fixes_d3labphys.csv"
REC_TEST = ROOT / "runs/test_v1_high_854/test/records"
F1280 = 722.0
DIST_KINDS = ("distance", "displacement", "path_length", "camera_distance")


def template():
    t = pd.read_csv(ROOT / "data/submission_template/quantiphy_submission_template.csv")
    t["cat"] = t.inference_type.str[0] + t.video_type.str[1]
    return t


def records(rec_dir=REC_TEST, prefix="captured_"):
    out = {}
    for f in sorted(glob.glob(str(Path(rec_dir) / f"{prefix}*.json"))):
        r = json.load(open(f))
        out[r["video_id"]] = r
    return out


def mra_item(pred, gt):
    rel = abs(pred - gt) / abs(gt)
    return sum(rel < 1 - th for th in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95)) / 10.0
