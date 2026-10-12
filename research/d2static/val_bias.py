"""EVALUATION ONLY (validation labels): signed log error of raw pipeline answers by category x target kind
x source, to test whether extent-vs-motion cross terms (S2 motion, D2 static) carry a shared extent bias."""
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from common import *

d = table("val_hires")
d["lr"] = np.log(d.raw / d.answer.astype(float))
d["item"] = mra_item(d.raw, d.answer.astype(float))
d["static"] = np.where(d.tkind.isin(["size", "distance"]), "static", "motion")
d["src"] = np.where(d.video_source.isin(["simulation", "segmentation"]), "sim", d.video_source)
g = d[d.category.isin(["S2", "D2"])].groupby(["category", "static", "src"])
print(g.agg(n=("lr", "size"), med_lr=("lr", "median"), mean_lr=("lr", "mean"), mad=("lr", lambda s: np.median(np.abs(s))),
            mra=("item", "mean")).round(3))
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 70)
x = d[(d.category == "S2")]
print(x[["video_id", "prior", "question", "answer", "raw", "lr", "method"]].round(3).to_string())
