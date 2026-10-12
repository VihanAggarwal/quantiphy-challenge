"""Shared table for the lab size study (research/labsize). Test INPUTS only (question / prior / depth_info
text, Claude records) plus our own cached answers; validation labels are read only by evaluate_val.py."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from qp.data import load_split  # noqa: E402
from qp.open.qwen_vl import parse_prior_text, parse_question_text  # noqa: E402
from qp import postprocess as pp  # noqa: E402

BASE = ROOT / "submissions/trackA_probe8_p7b_d2fixes_d3labphys.csv"
RAW = ROOT / "runs/test_v1_high_854/test.csv"
REC = {"test": ROOT / "runs/test_v1_high_854/test/records",
       "val_hires": ROOT / "runs/val_hr_v1_high/val_hires/records"}
RAWS = {"test": RAW, "val_hires": ROOT / "runs/val_hr_v1_high/val_hires.csv"}


def read_sub(p, idx=None):
    d = pd.read_csv(p, float_precision="round_trip")
    d = d.rename(columns={d.columns[0]: "id"}).set_index("id")
    return d if idx is None else d.reindex(idx)


def table(split="test", lab_only=True) -> pd.DataFrame:
    t = load_split(split).set_index("qid")
    if lab_only:
        t = t[(t.video_source == "lab") & (t.video_type.str[1] == "3")].copy()
    pq = t.question.map(parse_question_text)
    t["kind"] = pq.map(lambda p: p["kind"])
    t["objs"] = pq.map(lambda p: p["objects"])
    t["qtime"] = pq.map(lambda p: p["time"])
    t["dim"] = pq.map(lambda p: p["dimension"])
    pr = t.prior.map(lambda s: parse_prior_text(str(s).split("\n")[0]))
    t["pkind"] = pr.map(lambda p: p["kind"])
    t["pval"] = pr.map(lambda p: p["value_si"])
    t["pobjs"] = pr.map(lambda p: p["objects"])
    t["family"] = t.video_id.str.replace(r"^(captured_\d+[a-z]?)[sx]?$", r"\1", regex=True)
    return t


def records(split="test") -> dict:
    out = {}
    for p in sorted(REC[split].glob("*.json")):
        r = json.loads(p.read_text())
        if r and r.get("meta"):
            out[r["video_id"]] = r
    return out


THR = np.arange(0.50, 0.951, 0.05)


def mra(pred, gt) -> np.ndarray:
    """Per-item mean relative accuracy (QuantiPhy / VSI-Bench): mean over theta in .50:.95 of 1[|p-g|/g < 1-theta]."""
    p, g = np.asarray(pred, float), np.asarray(gt, float)
    e = np.abs(p - g) / np.abs(g)
    return (e[..., None] < (1 - THR)).mean(-1)


def render_event(video_id: str) -> str:
    return re.sub(r"^(captured_\d+[ab]?)[sxX]?$", r"\1", str(video_id))
