"""out/<split>/qwen_dyn.csv = qwen_dense solution with 2D motion-prior questions re-solved by prior_cands' choice.
    .venv/bin/python research/trackb_dense/make_dyn.py val|test [--base TAG] [--col value]"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tbcommon import OUT  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("split")
ap.add_argument("--base", default="")
ap.add_argument("--col", default="value")
ap.add_argument("--tag", default="qwen_dyn")
ap.add_argument("--only-solved", action="store_true", help="re-solve only questions the base solved")
a = ap.parse_args()
base = a.base or ("qwen_dense" if a.split == "val" else "qwen_dense_labfov")
g = pd.read_csv(OUT / a.split / f"{base}.csv").set_index("id")
R = pd.read_csv(OUT / a.split / "prior_cands.csv").set_index("id")
v = R[a.col].reindex(g.index)
has = v.notna() & (v > 0)
if a.only_solved:
    has &= g.geo_value.notna()
g.loc[has, "geo_value"] = v[has]
g.loc[has, "geo_si"] = np.nan          # unit-free here; GEO_MAX_SI checked on the base solution only
g.loc[has, "flags"] = g.loc[has, "flags"].fillna("") + ";prior_" + R["pick"].reindex(g.index)[has].astype(str)
g.reset_index().to_csv(OUT / a.split / f"{a.tag}.csv", index=False)
print(f"{a.tag}: {int(has.sum())} rows from prior candidates ({a.col})")
