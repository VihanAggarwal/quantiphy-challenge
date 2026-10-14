"""Validation questions scored with the FULL-RESOLUTION test-run outputs of trackb_v1 (the 24 validation clips are
test clips; 140 of 159 validation questions are also test questions). Matches (video_id, normalised question).
The Colab validation run used the 480p validation copies, the test run full-resolution videos, so this measures the
configuration that produced the test answers.

    .venv/bin/python research/trackb_next/diag_hires.py
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "research" / "trackb_dense"))
sys.path.insert(0, str(HERE))
warnings.filterwarnings("ignore")
from diagnose import CATS, items, macro, src_of  # noqa: E402
from qp import postprocess as pp  # noqa: E402
from tbcommon import RUN, base_preds, questions  # noqa: E402


def main():
    val, test = questions("val"), questions("test")
    key = dict(zip(zip(test.video_id, test.question.map(pp.norm_question)), test.qid))
    val["tqid"] = [key.get((v, pp.norm_question(q))) for v, q in zip(val.video_id, val.question)]
    m = val.tqid.notna()
    print(f"matched {int(m.sum())}/{len(val)} validation questions to test qids")
    V = val[m].reset_index(drop=True)
    tq = V.tqid.astype(int)
    Pv = {k: s.reindex(V.qid).to_numpy(float) for k, s in base_preds("val", V.qid).items()}
    Pt = {k: s.reindex(tq).to_numpy(float) for k, s in base_preds("test", tq).items()}
    for name, sub in (("qwen_geo_raw", "qwen"), ("cv_geo_raw", "cv"), ("cvq_geo_raw", "cvq")):
        for P, split, ids in ((Pv, "val", V.qid), (Pt, "test", tq)):
            d = pd.read_csv(RUN / split / sub / "geometry.csv").set_index("id")
            P[name] = d.geo_value.reindex(ids).to_numpy(float)
    y, c = V.answer.to_numpy(float), V.category.to_numpy()
    rows = []
    for k in ["caw", "qwen_direct", "qwen35", "gemma4", "qwen_geo", "cvq_geo", "qwen_geo_raw", "cvq_geo_raw", "cv_geo_raw"]:
        rows.append(dict(method=k, run="val480", **macro(items(Pv[k], y), c), cov=float(np.isfinite(Pv[k]).mean())))
        rows.append(dict(method=k, run="test_fullres", **macro(items(Pt[k], y), c), cov=float(np.isfinite(Pt[k]).mean())))
    print(pd.DataFrame(rows).set_index(["method", "run"]).round(3).to_string())


if __name__ == "__main__":
    main()
