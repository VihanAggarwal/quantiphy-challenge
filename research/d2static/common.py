"""Shared loaders for research/d2static (test inputs only; validation labels only in eval scripts)."""
from __future__ import annotations
import json, re, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp.data import load_split  # noqa: E402

BASE = ROOT / "submissions/trackA_probe8_p7b_d2fixes_d3labphys.csv"
REC = {"test": ROOT / "runs/test_v1_high_854/test/records",
       "val_hires": ROOT / "runs/val_hr_v1_high/val_hires/records"}
RAW = {"test": ROOT / "runs/test_v1_high_854/test.csv",
       "val_hires": ROOT / "runs/val_hr_v1_high/val_hires.csv"}


def records(split="test"):
    out = {}
    for p in sorted(REC[split].glob("*.json")):
        r = json.loads(p.read_text())
        if r and r.get("meta"):
            out[r["video_id"]] = r
    return out


def specs(recs):
    """qid -> question dict (spec, tracks, direct_answer) from the cached Claude records."""
    out = {}
    for v, r in recs.items():
        for q in (r.get("parsed") or {}).get("questions", []) or []:
            out[int(q["qid"])] = dict(q, video_id=v)
    return out


def table(split="test"):
    df = load_split(split).set_index("qid")
    raw = pd.read_csv(RAW[split]).set_index("id")
    df["raw"] = raw.parsed_value
    df["geo"] = raw.geo_value
    df["direct"] = raw.direct_value
    df["method"] = raw.method
    if split == "test":
        b = pd.read_csv(BASE).set_index("id")["parsed_value"]
        df["p8"] = b
    sp = specs(records(split))
    df["tkind"] = [((sp.get(q) or {}).get("spec") or {}).get("target", {}).get("kind") for q in df.index]
    df["pkind"] = [((sp.get(q) or {}).get("spec") or {}).get("prior", {}).get("kind") for q in df.index]
    df["ptime"] = [((sp.get(q) or {}).get("spec") or {}).get("prior", {}).get("time") for q in df.index]
    return df


def mra_item(pred, gt):
    pred = np.asarray(pred, float); gt = np.asarray(gt, float)
    rel = np.abs(pred - gt) / np.abs(gt)
    th = np.arange(0.5, 1.0, 0.05)
    return np.mean([(rel < 1 - t) for t in th], axis=0)
