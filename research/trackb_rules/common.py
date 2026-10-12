"""Shared inputs for the Track B rule study (research/trackb_rules).

Track B answers = log-median of the four open-weight methods (scripts/trackb_build.py --combine median).
Validation evaluation: the validation questions are put back into the test question table (all 24 validation
videos are test videos), replacing the test rows that repeat them (same clip and question), so a validation row
sees exactly the family links a test row would. Validation labels are read ONLY by `score_val`; the rules never
see them (qp.postprocess drops any answer column on entry).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp.data import load_split, load_validation  # noqa: E402
from qp.mra import item_scores  # noqa: E402
from qp import postprocess as pp  # noqa: E402

RUN = Path("/tmp/claude-0/tb2/x/trackb_v1")
METHODS = ["qwen/direct.csv", "caw/caw.csv", "qwen/geometry.csv", "cv/geometry.csv"]
VAL_OFFSET = 100000
CATS = ("S2", "D2", "S3", "D3")


def read(path: Path, index) -> pd.Series:
    d = pd.read_csv(path)
    s = d.rename(columns={d.columns[0]: "id"}).set_index("id")["parsed_value"]
    s = pd.to_numeric(s, errors="coerce").abs()
    return s.where(np.isfinite(s) & (s > 0)).reindex(index)


def median4(split: str, index) -> pd.Series:
    L = np.log(np.vstack([read(RUN / split / m, index).to_numpy() for m in METHODS]))
    with np.errstate(all="ignore"):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return pd.Series(np.exp(np.nanmedian(L, 0)), index=index)


def combined():
    """(questions without answers, predictions, val labels by offset qid, val qids offset).
    Test rows repeating a validation question (same clip, normalised question) are dropped."""
    test = load_split("test")
    val = load_validation()
    pt = median4("test", test.qid)
    pv = median4("val", val.qid)
    vkey = set(zip(val.video_id, val.question.map(pp.norm_question)))
    dup = [(v, pp.norm_question(q)) in vkey for v, q in zip(test.video_id, test.question)]
    test_kept = test[~np.array(dup)]
    paths = dict(zip(test.video_id, test.video_path))
    v2 = val.drop(columns=["answer"]).copy()
    v2["qid"] = v2.qid + VAL_OFFSET
    v2["video_path"] = v2.video_id.map(paths).fillna(v2.video_path)
    df = pd.concat([test_kept, v2[test_kept.columns]], ignore_index=True)
    pred = pd.concat([pt.reindex(test_kept.qid), pd.Series(pv.to_numpy(), index=val.qid + VAL_OFFSET)])
    labels = pd.Series(val.answer.to_numpy(float), index=val.qid + VAL_OFFSET)
    cat = pd.Series(val.category.to_numpy(), index=labels.index)
    return df, pred, labels, cat, int(np.sum(dup))


def score_val(pred: pd.Series, labels: pd.Series, cat: pd.Series) -> dict:
    it = pd.Series(item_scores(pred.reindex(labels.index).to_numpy(), labels.to_numpy()), index=labels.index)
    it = it.fillna(0.0)
    per = {c: float(it[cat == c].mean()) for c in CATS}
    return dict(MRA=float(np.mean(list(per.values()))), **per, items=it)
