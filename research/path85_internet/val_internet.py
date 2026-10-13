"""Validation internet rows (labels for EVALUATION ONLY): per-row errors of the v1-high run (geo / direct)."""
import sys; sys.path.insert(0,'.')
import pandas as pd, numpy as np
from qp.data import load_validation
from qp.mra import item_scores
v = load_validation()
r = pd.read_csv("runs/val_hr_v1_high/val_hires.csv").set_index("id")
v["geo"]=v.qid.map(r.geo_value); v["direct"]=v.qid.map(r.direct_value); v["pv"]=v.qid.map(r.parsed_value)
s = v[v.video_id.str.startswith("internet")].copy()
s["s_pv"]=item_scores(s.pv, s.answer); s["s_geo"]=item_scores(s.geo.fillna(s.pv), s.answer); s["s_dir"]=item_scores(s.direct.fillna(s.pv), s.answer)
s["lr"]=np.log(s.pv/s.answer)
pd.set_option("display.width",250); pd.set_option("display.max_colwidth",90)
print(s[["video_id","category","prior","question","answer","pv","geo","direct","lr","s_pv","s_dir"]].to_string())
print(s.groupby("category")[["s_pv","s_geo","s_dir"]].mean())
