"""Dump all lab 3D test rows with the current best (physb2) answer, raw pipeline values and parse fields."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "research/labsize"))
import common as C
t = C.table("test")
best = C.read_sub(ROOT / "submissions/trackA_cand_physb2_on_p21.csv", t.index).parsed_value
raw = pd.read_csv(ROOT / "runs/test_v1_high_854/test.csv").set_index("id").reindex(t.index)
p8 = C.read_sub(ROOT / "submissions/trackA_probe8_p7b_d2fixes_d3labphys.csv", t.index).parsed_value
t["best"] = best; t["raw"] = raw.parsed_value; t["geo"] = raw.geo_value; t["direct"] = raw.direct_value; t["method"] = raw.method
t["p8"] = p8
t["r_best_raw"] = t.best / t.raw
t["cat"] = t.category
from qp.data import load_split
vv = load_split("val_hires")
vkeys = set(zip(vv.video_id, vv.question.str.strip().str.lower()))
t["val_overlap"] = [(a, b.strip().lower()) in vkeys for a, b in zip(t.video_id, t.question)]
t.to_pickle(Path(__file__).parent / "out/labtable.pkl")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 900); pd.set_option("display.max_colwidth", 70)
print(t.groupby(["cat", "kind"]).size())
print(t.groupby(["cat", "pkind"]).size())
