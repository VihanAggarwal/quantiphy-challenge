"""Validation check of the open-track lab label-noise factor (labnoise_open.factors) on lab motion rows.

    .venv/bin/python research/trackb_dense/eval_labnoise.py [--sz 0.02] [--szL 0.02]
Base answers: the v3 per-category median sets (and each single method). Labels used for scoring only."""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import labnoise_open as LN  # noqa: E402
from select_sets import V3, all_methods  # noqa: E402
from tbcommon import CATS, item, log_median, questions  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--sz", type=float, default=0.02)
ap.add_argument("--szL", type=float, default=0.02)
a = ap.parse_args()
val = questions("val")
P = all_methods("val", val)
v3 = pd.Series(np.nan, index=val.index)
for c in CATS:
    m = val.category == c
    v3[m] = log_median([P[x] for x in V3[c]])[m]
cands = {"v3": v3, "caw": P["caw"], "cv_geo": P["cv_geo"], "qwen_geo": P["qwen_geo"]}
for src in ("qwen", "cv"):
    for name, ans in cands.items():
        A = pd.Series(ans.to_numpy(), index=val.qid)
        F = LN.factors("val", src, A, a.sz, a.szL).set_index("id")
        rows = F.index[F.kind != "acceleration"]
        vv = val.set_index("qid").loc[rows]
        base = item(A.loc[rows], vv.answer)
        new = item(A.loc[rows] * F.factor.loc[rows], vv.answer)
        cat = vv.category
        print(f"[{src} tracks] {name:9s} lab motion (no accel) n={len(rows)} changed={int((F.factor.loc[rows] != 1).sum())} "
              f"base {base.mean():.3f} -> {new.mean():.3f} | " +
              " ".join(f"{c} {base[cat == c].mean():.3f}->{new[cat == c].mean():.3f} (n={int((cat == c).sum())})"
                       for c in ("S3", "D3")) + f" | factors {F.factor.loc[rows][F.factor.loc[rows] != 1].round(2).tolist()}")
