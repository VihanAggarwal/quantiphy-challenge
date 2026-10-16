"""Residual-error tables for the agent answers on non-lab clips.

VAL: the 159 validation questions (24 pilot clips), with label, agent pass 1 (/tmp/blind), agent pass 2 (/tmp/blind_r2,
     12 sim clips), combo3 (matched test row), Claude 3-run direct median (dmed), Sol direct (runs/val_sol_high).
FACT: test rows with an exact stated fact from a sibling clip's prior (held out from the agent), with the agent answer
     (/tmp/blind_test), the pre-agent base (C1_solS2S3), combo3, dmed, Sol (runs/test_sol_high), and the current best upload.
Labels on validation are read only to measure; nothing here writes a test answer.

    .venv/bin/python research/next/nlres/tables.py   -> research/next/nlres/val.pkl, fact.pkl
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from qp import postprocess as pp  # noqa: E402
from qp.data import load_split  # noqa: E402

OUT = Path(__file__).resolve().parent


def answers(root, videos=None):
    out = {}
    root = Path(root)
    for vd in sorted(p for p in root.iterdir() if p.is_dir()):
        if videos is not None and vd.name not in videos:
            continue
        f = vd / "answers.json"
        if not f.exists():
            continue
        try:
            for k, x in json.loads(f.read_text()).items():
                try:
                    val = abs(float(x))
                except (TypeError, ValueError):
                    continue
                if np.isfinite(val) and val > 0:
                    out[(vd.name, int(k))] = val
        except json.JSONDecodeError:
            pass
    return out


def col(path, name="parsed_value"):
    d = pd.read_csv(path)
    d = d.rename(columns={d.columns[0]: "id"}).set_index("id")
    c = name if name in d.columns else "parsed_value"
    s = pd.to_numeric(d[c], errors="coerce")
    return s.where(s > 0)


def qkind(q: str) -> str:
    q = q.lower()
    if "acceler" in q:
        return "accel"
    if "speed" in q or "velocity" in q:
        return "speed"
    if "distance" in q or "how far" in q or "displacement" in q or "travel" in q:
        return "dist"
    return "size"


def ctype(video_type: str, src: str, vid: str) -> str:
    if src == "lab" or vid.startswith("captured"):
        return "lab"
    if src == "internet" or vid.startswith("internet"):
        return "internet"
    return "sim3" if video_type[1] == "3" else "sim2"


def build_val():
    v = load_split("val_hires").set_index("qid")
    t = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
    key = {(a, pp.norm_question(b)): i for i, a, b in zip(t.index, t.video_id, t.question)}
    v["tq"] = [key.get((a, pp.norm_question(b))) for a, b in zip(v.video_id, v.question)]
    a1 = answers("/tmp/blind", set(v.video_id))
    a2 = answers("/tmp/blind_r2", set(v.video_id)) if Path("/tmp/blind_r2").exists() else {}
    v["agent"] = [a1.get((vid, q), np.nan) for vid, q in zip(v.video_id, v.index)]
    v["agent2"] = [a2.get((vid, q), np.nan) for vid, q in zip(v.video_id, v.index)]
    v["combo3"] = [t.combo3.get(i) if i is not None else np.nan for i in v.tq]
    v["tsrc"] = [t.srcg.get(i) if i is not None else None for i in v.tq]
    L = np.log(pd.concat([col(ROOT / p, "direct_value").reindex(v.index) for p in
                          ("runs/val_hr_v1_high/val_hires.csv", "runs/val_hr_v2_high/val_hires.csv", "runs/val_opus_high/val.csv")],
                         axis=1))
    v["dmed"] = np.exp(L.median(axis=1))
    v["sol"] = col(ROOT / "runs/val_sol_high/val_hires.csv", "direct_value").reindex(v.index)
    v["pipe"] = col(ROOT / "runs/val_hr_v1_high/val_hires.csv", "parsed_value").reindex(v.index)
    v["gt"] = v.answer.astype(float)
    v["kind"] = v.question.map(qkind)
    v["ctype"] = [ctype(a, b, c) for a, b, c in zip(v.video_type, v.video_source, v.video_id)]
    v["seg"] = v.video_id.str.endswith("_segmented")
    return v


def build_fact():
    t = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
    f = t[t.fact.notna()].copy()
    ag = answers("/tmp/blind_test")
    f["agent"] = [ag.get((vid, i), np.nan) for vid, i in zip(f.video_id, f.index)]
    # segmented twins take the original's answer (as in build_agent_sub.py)
    orig = {(vv, pp.norm_question(q)): i for i, vv, q in zip(t.index, t.video_id, t.question) if not vv.endswith("_segmented")}
    for i in f.index[f.agent.isna()]:
        vv, q = f.at[i, "video_id"], f.at[i, "question"]
        if vv.endswith("_segmented"):
            j = orig.get((vv[: -len("_segmented")], pp.norm_question(q)))
            if j is not None:
                f.at[i, "agent"] = ag.get((vv[: -len("_segmented")], j), np.nan)
    f["c1"] = col(ROOT / "submissions/trackA_cand_C1_solS2S3.csv").reindex(f.index)
    f["best"] = col(ROOT / "submissions/trackA_probe_agent_sim2agent.csv").reindex(f.index)
    f["sol"] = col(ROOT / "runs/test_sol_high/test.csv", "direct_value").reindex(f.index)
    f["raw"] = t.r_parsed_value.where(~(t.category.isin(["S3", "D3"]) & t.srcg.eq("sim")), t.dmed).reindex(f.index)
    f["gt"] = f.fact.astype(float)
    f["qkind"] = f.question.map(qkind)
    f["ctype"] = [ctype(a, b, c) for a, b, c in zip(f.video_type, f.srcg, f.video_id)]
    f["seg"] = f.video_id.str.endswith("_segmented")
    return f


if __name__ == "__main__":
    v = build_val()
    v.to_pickle(OUT / "val.pkl")
    f = build_fact()
    f.to_pickle(OUT / "fact.pkl")
    print("val", v.shape, v.agent.notna().sum(), v.groupby("ctype").size().to_dict())
    print("fact", f.shape, f.agent.notna().sum(), f.groupby("ctype").size().to_dict())
