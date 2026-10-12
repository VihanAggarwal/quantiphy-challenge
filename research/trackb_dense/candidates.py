"""Principled per-category member sets (v3 plus a-priori substitutions), scored on validation (in-sample for v3,
whose sets were picked on it) and on the test stated-fact rows.

    .venv/bin/python research/trackb_dense/candidates.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eval_facts_methods import fact_labels, table  # noqa: E402
from select_sets import V3, all_methods  # noqa: E402
from tbcommon import CATS, item, log_median, questions  # noqa: E402

FOV = {"qwen_geo": "qwen_fov", "cv_geo": "cv_fov", "cvq_geo": "cvq_fov"}   # lab camera prior (3D lab only)


def fov(sets):
    return {c: [FOV.get(m, m) for m in v] for c, v in sets.items()}


def plus(sets, *ms, cats=CATS):
    return {c: v + [m for m in ms if m not in v] if c in cats else v for c, v in sets.items()}


def sub(sets, a, b, cats=CATS):
    return {c: [b if m == a and c in cats else m for m in v] for c, v in sets.items()}


SETS = {
    "v3": V3,
    "v3 fov": fov(V3),
    "v3 +cvq": plus(V3, "cvq_geo"),
    "v3 fov +cvq": fov(plus(V3, "cvq_geo")),
    "v3 fov +cvq +qwen35": fov(plus(V3, "cvq_geo", "qwen35")),
    "v3 fov cv->cvq": fov(sub(V3, "cv_geo", "cvq_geo")),
    "v3 fov cv->cvq +qwen35": fov(plus(sub(V3, "cv_geo", "cvq_geo"), "qwen35")),
    "v3 fov cv->cvq, 2D qwen->dense": sub(fov(sub(V3, "cv_geo", "cvq_geo")), "qwen_fov", "qwen_dense", ("S2", "D2")),
    "v3 fov cv->cvq +qwen35(3D)": fov(plus(sub(V3, "cv_geo", "cvq_geo"), "qwen35", cats=("S3", "D3"))),
    "v3 fov +cvq +qwen35(3D)": fov(plus(V3, "cvq_geo", "qwen35", cats=("S3", "D3"))),
    "v3 fov +cvq(all) +qwen35(3D) +gemma4(3D)": fov(plus(plus(V3, "cvq_geo"), "qwen35", "gemma4", cats=("S3", "D3"))),
}


def val_scores(P, val):
    rows = {}
    for name, st in SETS.items():
        r = {}
        for c in CATS:
            m = (val.category == c).to_numpy()
            r[c] = item(log_median([P[x] for x in st[c]]), val.answer)[m].mean()
        r["MRA"] = float(np.mean([r[c] for c in CATS]))
        rows[name] = r
    return pd.DataFrame(rows).T


if __name__ == "__main__":
    val = questions("val")
    print("VALIDATION"); print(val_scores(all_methods("val", val), val).round(4).to_string())
    test = questions("test")
    try:
        P = all_methods("test", test)
        T = table(SETS, P, test, fact_labels())
        print("TEST STATED FACTS"); print(T[[i.startswith("SET") or i == "n" for i in T.index]].round(3).to_string())
    except Exception as e:  # noqa: BLE001
        print("test facts skipped:", e)
