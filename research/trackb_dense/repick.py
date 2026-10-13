"""Re-run prior_motion.choose on prior_cands.csv with a reduced candidate set (no re-tracking).
    .venv/bin/python research/trackb_dense/repick.py val|test --drop klt,mask --col value_nokltmask"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prior_motion as PM  # noqa: E402
from tbcommon import OUT  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("split")
ap.add_argument("--drop", default="klt,mask")
ap.add_argument("--col", default="value2")
a = ap.parse_args()
f = OUT / a.split / "prior_cands.csv"
R = pd.read_csv(f)
drop = set(a.drop.split(",")) | {"sparse"}
names = [c[3:] for c in R.columns if c.startswith("px_") and c[3:] not in drop]
vals, picks = [], []
for _, r in R.iterrows():
    est = {n: r[f"px_{n}"] for n in names if np.isfinite(r.get(f"px_{n}", np.nan)) and np.isfinite(r.get(f"v_{n}", np.nan))}
    p, _ = PM.choose(est)
    picks.append(p)
    vals.append(r[f"v_{p}"] if p else np.nan)
R[a.col], R["pick_" + a.col] = vals, picks
R.to_csv(f, index=False)
print(a.split, pd.Series(picks).value_counts(dropna=False).to_dict())
