"""Shared helpers of research/trackb_agent (CPU only): clip types, agent answers, base tables, the routing rule."""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TYPES = ("sim3", "sim2", "internet", "lab")
MARGIN = 0.02            # pre-registered (RESULT.md): agent if >= base + MARGIN, gm if within MARGIN, base otherwise


def clip_type(video_source: str, video_type: str) -> str:
    """research/blind/build_agent_sub.py's type logic on the question inputs: internet and lab by video_source, every
    other source (simulation, segmentation - including segmented internet clips, as srcg in the r86 master table) is
    a simulation, split by video_type[1] into sim3 / sim2."""
    src = str(video_source or "").strip().lower()
    if src == "internet":
        return "internet"
    if src == "lab":
        return "lab"
    return "sim3" if str(video_type)[1:2] == "3" else "sim2"


def agent_answers(split_dir: Path) -> tuple[pd.Series, pd.Series, dict]:
    """(answer by qid, source by qid, per-video records) from <split_dir>/answers/*.json (run_agent output)."""
    vals, srcs, recs = {}, {}, {}
    d = Path(split_dir) / "answers"
    for p in sorted(d.glob("*.json")) if d.exists() else []:
        try:
            rec = json.loads(p.read_text())
        except ValueError:
            print("bad json", p)
            continue
        if not isinstance(rec, dict) or rec.get("status") != "done":
            continue
        recs[str(rec.get("video_id"))] = rec
        for q, x in (rec.get("answers") or {}).items():
            try:
                v = abs(float(x))
            except (TypeError, ValueError):
                continue
            if math.isfinite(v) and v > 0:
                vals[int(q)] = v
                srcs[int(q)] = (rec.get("source") or {}).get(str(q), "agent")
    return pd.Series(vals, dtype=float), pd.Series(srcs, dtype=object), recs


def gm(a: pd.Series, b: pd.Series) -> pd.Series:
    """geometric mean where both exist, else whichever exists"""
    a, b = a.astype(float), b.astype(float)
    both = (a > 0) & (b > 0)
    out = a.where(a > 0, b)
    out[both] = np.exp((np.log(a[both]) + np.log(b[both])) / 2)
    return out


def routed(base: pd.Series, agent: pd.Series, types: pd.Series, stated: pd.Series, decision: dict) -> pd.Series:
    """Apply per-type decisions ("agent" / "gm" / "base"); rows set by a stated-fact rule always keep the base."""
    out = base.astype(float).copy()
    ag = agent.reindex(base.index)
    st = stated.reindex(base.index).fillna(0).astype(bool)
    for t, how in decision.items():
        m = (types.reindex(base.index) == t) & ~st & ag.notna()
        if how == "agent":
            out[m] = ag[m]
        elif how == "gm":
            out[m] = gm(ag[m], base[m])
    return out


def decide(score_agent: float, score_base: float, n_agent: int, margin: float = MARGIN) -> str:
    """The pre-registered rule (RESULT.md), per type, on validation item MRA (agent rows filled with the base)."""
    if n_agent == 0 or not np.isfinite(score_agent):
        return "base"
    d = score_agent - score_base
    if d >= margin - 1e-12:
        return "agent"
    if d > -margin + 1e-12:
        return "gm"
    return "base"


def load_base(name: str) -> pd.DataFrame:
    return pd.read_csv(HERE / name)
