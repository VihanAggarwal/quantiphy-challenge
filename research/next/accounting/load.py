"""Shared loaders for the lever accounting (research/next/accounting).  No labels are read here."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
SUB = ROOT / "submissions"


def master() -> pd.DataFrame:
    t = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
    t["kind4"] = np.where(t.srcg.eq("sim") & t.video_type.str[1].eq("3"), "sim3",
                          np.where(t.srcg.eq("sim") & t.video_type.str[1].eq("2"), "sim2",
                                   np.where(t.srcg.eq("internet"), "internet", "lab")))
    return t


def read(name: str, index) -> pd.Series:
    p = Path(name) if "/" in name else SUB / (name if name.endswith(".csv") else name + ".csv")
    d = pd.read_csv(p)
    return d.rename(columns={d.columns[0]: "id"}).set_index("id")["parsed_value"].astype(float).reindex(index)


def agent_answers(index, t, root=ROOT / "research/blind/out/blind_test") -> pd.Series:
    """Raw agent answer per qid (abs), segmented twins filled from the original (as build_agent_sub.py)."""
    from qp import postprocess as pp
    ag = {}
    for vd in sorted(p for p in Path(root).iterdir() if p.is_dir()):
        f = vd / "answers.json"
        if not f.exists():
            continue
        try:
            js = json.loads(f.read_text())
        except json.JSONDecodeError:
            continue
        for k, x in js.items():
            try:
                v = abs(float(x))
            except (TypeError, ValueError):
                continue
            if np.isfinite(v) and v > 0:
                ag[(vd.name, int(k))] = v
    ans = pd.Series(np.nan, index=index)
    for i, v in zip(t.index, t.video_id):
        x = ag.get((v, i))
        if x is not None:
            ans[i] = x
    orig = {(v, pp.norm_question(q)): i for i, v, q in zip(t.index, t.video_id, t.question) if not v.endswith("_segmented")}
    for i, v, q in zip(t.index, t.video_id, t.question):
        if v.endswith("_segmented") and np.isnan(ans[i]):
            j = orig.get((v[: -len("_segmented")], pp.norm_question(q)))
            if j is not None and not np.isnan(ans.get(j, np.nan)):
                ans[i] = ans[j]
    return ans


def same(a, b, rtol=1e-6):
    return np.isclose(a, b, rtol=rtol, atol=0)
