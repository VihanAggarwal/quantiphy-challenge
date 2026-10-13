"""EVALUATION ONLY: score the current best (physb2) on the lab validation questions via the test overlap rows."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from qp.data import load_split
from qp.mra import item_scores
t = pd.read_pickle(Path(__file__).parent / "out/labtable.pkl")
v = load_split("val_hires")
v = v[v.video_source == "lab"].copy()
key = {(a, b.strip().lower()): q for q, a, b in zip(t.index, t.video_id, t.question)}
v["tq"] = [key.get((a, b.strip().lower())) for a, b in zip(v.video_id, v.question)]
v = v[v.tq.notna()].copy(); v.tq = v.tq.astype(int)
for c in ("best", "raw", "geo", "direct", "kind", "src"):
    v[c] = t.loc[v.tq, c].to_numpy()
for c in ("best", "raw", "geo", "direct"):
    v["s_" + c] = item_scores(v[c], v.answer)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 80)
v["q"] = v.question.str.extract(r"((?:What|what|How|how)[^?]*\?)")[0].str.slice(0, 70)
print(v[["video_id", "category", "kind", "q", "answer", "best", "geo", "direct", "src", "s_best", "s_geo", "s_direct"]].round(3).to_string())
print(v.groupby(["category", "kind"])[["s_best", "s_geo", "s_direct"]].agg(["mean", "size"]).round(3))
v.to_pickle(Path(__file__).parent / "out/val_lab.pkl")
