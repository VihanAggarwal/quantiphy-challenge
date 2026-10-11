"""Shared table for the 3D simulation / segmentation (non-lab) audit. Test INPUTS only (questions, priors,
depth_info) plus our own cached answers; validation labels are read only by evaluate_val.py."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp.data import load_split  # noqa: E402
from qp.open.qwen_vl import parse_prior_text, parse_question_text  # noqa: E402
from qp import postprocess as pp  # noqa: E402

BASE = ROOT / "submissions/trackA_probe8_p7b_d2fixes_d3labphys.csv"
RUNS = ["runs/test_v1_high_854/test.csv", "runs/test_3dnl_v1_high_b/test.csv", "runs/test_3dnl_v2_high/test.csv"]


def read_sub(p, idx):
    d = pd.read_csv(p, float_precision="round_trip")
    d = d.rename(columns={d.columns[0]: "id"}).set_index("id")
    return d.reindex(idx)


def depth_tracks(text: str) -> dict:
    return pp._depth_entries(text)


def table(split="test") -> pd.DataFrame:
    t = load_split(split).set_index("qid")
    t = t[(t.video_type.str[1] == "3") & (t.video_source != "lab")].copy()
    pq = t.question.map(parse_question_text)
    t["kind"] = pq.map(lambda p: p["kind"])
    t["objs"] = pq.map(lambda p: p["objects"])
    t["qtime"] = pq.map(lambda p: p["time"])
    t["qwin"] = pq.map(lambda p: p["window"])
    t["dim"] = pq.map(lambda p: p["dimension"])
    pr = t.prior.map(lambda s: parse_prior_text(str(s).split("\n")[0]))
    t["pkind"] = pr.map(lambda p: p["kind"])
    t["pval"] = pr.map(lambda p: p["value_si"])
    t["pobjs"] = pr.map(lambda p: p["objects"])
    return t


def answers(t: pd.DataFrame) -> pd.DataFrame:
    idx = t.index
    out = pd.DataFrame(index=idx)
    out["p8"] = read_sub(BASE, idx).parsed_value.astype(float)
    for i, r in enumerate(RUNS):
        d = read_sub(ROOT / r, idx)
        out[f"d{i}"] = d.direct_value.astype(float)
        if i == 0:
            out["geo0"] = d.geo_value.astype(float)
            out["method0"] = d.method
            out["raw0"] = d.parsed_value.astype(float)
    out["dmed"] = np.exp(np.log(out[["d0", "d1", "d2"]]).median(axis=1))
    return out
