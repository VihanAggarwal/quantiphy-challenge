"""Validation check of the labsize candidates (labels used for EVALUATION ONLY: nothing here feeds
build_candidate.py). Validation clips are test clips, so the test rows whose (video, question) equal a
validation question are scored against its label, probe 8 vs candidate. Those test rows are among the
organizers' excluded overlap, so this is a premise check, not a leaderboard estimate.

    .venv/bin/python research/labsize/evaluate_val.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import BASE, ROOT, load_split, mra, read_sub  # noqa: E402

if __name__ == "__main__":
    v = load_split("val_hires")
    t = load_split("test")
    t["qn"] = t.question.str.strip().str.lower()
    v["qn"] = v.question.str.strip().str.lower()
    m = v.merge(t[["qid", "video_id", "qn"]], on=["video_id", "qn"], suffixes=("_val", ""))
    p8 = read_sub(BASE).parsed_value.astype(float)
    for name in ("main", "wb"):
        c = read_sub(ROOT / f"submissions/trackA_cand_labsize_{name}_on_p8.csv").parsed_value.astype(float)
        mm = m[(p8[m.qid].values != c[m.qid].values)].copy()
        mm["p8"] = p8[mm.qid].values
        mm["cand"] = c[mm.qid].values
        mm["s_p8"] = mra(mm.p8, mm.answer)
        mm["s_cand"] = mra(mm.cand, mm.answer)
        print(f"== {name}: {len(mm)} validation-identical test rows changed")
        print(mm[["qid", "video_id", "question", "answer", "p8", "cand", "s_p8", "s_cand"]].round(3).to_string())
        if len(mm):
            print("mean MRA p8 %.3f -> cand %.3f" % (mm.s_p8.mean(), mm.s_cand.mean()))
