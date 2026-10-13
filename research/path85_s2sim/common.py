"""Shared loaders for the S2 simulation study (test inputs + cached runs; no API)."""
from __future__ import annotations
import re, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp.data import load_test, load_validation  # noqa
BASE = ROOT / "submissions/trackA_cand_physb2_on_p21.csv"
RUN = ROOT / "runs/test_v1_high_854/test.csv"

def qkind(q: str) -> str:
    s = q.lower()
    if "acceleration" in s: return "acc"
    if "distance" in s: return "dist"
    if re.search(r"average (speed|velocity)", s) or "mean speed" in s: return "avgspeed"
    if "speed" in s or "velocity" in s: return "speed"
    return "size"

def test_table() -> pd.DataFrame:
    t = load_test().set_index("qid")
    sub = pd.read_csv(BASE).set_index("id")
    run = pd.read_csv(RUN).set_index("id")
    t["base"] = sub.parsed_value.reindex(t.index)
    for c in ("parsed_value", "geo_value", "direct_value", "method", "flags"):
        t["run_" + c] = run[c].reindex(t.index)
    t["kind"] = [qkind(q) for q in t.question]
    t["prior_kind"] = [qkind(p) if re.search(r"speed|velocity|acceleration", p, re.I) else "size" for p in t.prior]
    t["raw_in_base"] = np.isclose(t.base, t.run_parsed_value, rtol=1e-9)
    return t
