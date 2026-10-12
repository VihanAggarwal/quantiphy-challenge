"""Validation MRA (with qp.postprocess preset 'trackb') of fixed median sets on a Colab run (default tb3).

    .venv/bin/python research/trackb_v4/eval_sets.py [RUN_DIR]

Validation rows are put into the test question table (research/trackb_rules/common.py) so the family rules see
the same links as on test; labels are read only for scoring."""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "trackb_rules"))
import common  # noqa: E402
from common import CATS, VAL_OFFSET, load_split, pp, score_val  # noqa: E402
from qp.data import load_validation  # noqa: E402

F = {"caw": "caw/caw.csv", "cv_geo": "cv/geometry.csv", "qwen_geo": "qwen/geometry.csv",
     "qwen_direct": "qwen/direct.csv", "cvq_geo": "cvq/geometry.csv", "qwen35": "qwen35/direct.csv",
     "gemma4": "gemma4/direct.csv"}
RUN = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/claude-0/tb3/x/trackb_v1")


def med(split, idx, members):
    L = np.log(np.vstack([common.read(RUN / split / F[m], idx).to_numpy() for m in members]))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return pd.Series(np.exp(np.nanmedian(L, 0)), index=idx)


def table():
    test, val = load_split("test"), load_validation()
    vkey = set(zip(val.video_id, val.question.map(pp.norm_question)))
    dup = np.array([(v, pp.norm_question(q)) in vkey for v, q in zip(test.video_id, test.question)])
    tk = test[~dup]
    paths = dict(zip(test.video_id, test.video_path))
    v2 = val.drop(columns=["answer"]).copy()
    v2["qid"] = v2.qid + VAL_OFFSET
    v2["video_path"] = v2.video_id.map(paths).fillna(v2.video_path)
    df = pd.concat([tk, v2[tk.columns]], ignore_index=True)
    lab = pd.Series(val.answer.to_numpy(float), index=val.qid + VAL_OFFSET)
    cat = pd.Series(val.category.to_numpy(), index=lab.index)
    return test, val, tk, df, lab, cat


def preds(test, val, tk, sets):
    """sets: list of members, or dict category -> members."""
    def one(split, frame):
        if isinstance(sets, dict):
            out = pd.Series(np.nan, index=frame.qid)
            for c, ms in sets.items():
                m = (frame.category == c).to_numpy()
                out[m] = med(split, frame.qid, ms)[m].to_numpy()
            return out
        return med(split, frame.qid, sets)
    pv = one("val", val)
    return pd.concat([one("test", tk), pd.Series(pv.to_numpy(), index=val.qid + VAL_OFFSET)])


SETS = {
    "old4": ["qwen_direct", "caw", "qwen_geo", "cv_geo"],
    "all7": list(F),
    "3geo3dir": ["cv_geo", "cvq_geo", "qwen_geo", "caw", "qwen35", "gemma4"],
    "3geo4dir": ["cv_geo", "cvq_geo", "qwen_geo", "caw", "qwen35", "gemma4", "qwen_direct"],
    "2geo3dir": ["cvq_geo", "qwen_geo", "caw", "qwen35", "gemma4"],
    "cvq_caw_q35": ["cvq_geo", "caw", "qwen35"],
    "v3cat": {"S2": ["caw", "cv_geo", "qwen_direct"], "D2": ["qwen_direct", "caw", "qwen_geo", "cv_geo"],
              "S3": ["cv_geo", "qwen_geo", "qwen_direct"], "D3": ["caw", "qwen_geo", "qwen_direct"]},
}

if __name__ == "__main__":
    test, val, tk, df, lab, cat = table()
    for name, s in SETS.items():
        p = preds(test, val, tk, s)
        r0 = score_val(p, lab, cat)
        new, _ = pp.apply_rules(p, df, **pp.PRESETS["trackb"])
        r1 = score_val(new, lab, cat)
        print(f"{name:12s} raw {r0['MRA']:.4f} | +rules {r1['MRA']:.4f}  " + " ".join(f"{c} {r1[c]:.3f}" for c in CATS))
