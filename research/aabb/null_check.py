"""Run-to-run noise reference for the pilot's kill-test statistic: the same statistic between existing runs.

    .venv/bin/python research/aabb/null_check.py
"""
import json
import sys
from itertools import permutations
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))
from qp.data import load_split  # noqa: E402
from qp.mra import item_scores  # noqa: E402
from step1_bias import dim_word  # noqa: E402

v = load_split("val_hires")
v = v[(v.video_type.str[1] == "3") & (v.video_source != "lab")].set_index("qid")
gt = v.answer.astype(float)
vid = v.video_id.str.replace("_segmented", "", regex=False)
q = v.question
size = (q.map(dim_word) != "other") & ~q.str.contains(r"distance|above the|clear height", case=False)


def d(p):
    return pd.to_numeric(pd.read_csv(ROOT / p).set_index("id").direct_value, errors="coerce").reindex(gt.index)


R = {"hr_v1": d("runs/val_hr_v1_high/val_hires.csv"), "hr_v2": d("runs/val_hr_v2_high/val_hires.csv"),
     "opus_v1": d("runs/val_opus_high/val.csv")}
new = {}
for f in (Path(__file__).parent / "out").glob("*.json"):
    new.update({int(k): x for k, x in json.loads(f.read_text())["direct"].items() if x is not None})
R["aabb"] = pd.Series(new, dtype=float).reindex(gt.index)
S = {k: pd.Series(np.nan_to_num(item_scores(s.to_numpy(float), gt.to_numpy()), nan=0.0), index=gt.index)
     for k, s in R.items()}
print("pair (a - b)            all52    size30   other22   clips a better / changed")
for a, b in permutations(R, 2):
    if b != "hr_v1" and a != "aabb":
        continue
    dd = S[a] - S[b]
    bc = dd.groupby(vid).mean()
    ch = bc[bc.abs() > 1e-9]
    print(f"{a:8s} - {b:8s}   {dd.mean():+.4f}  {dd[size].mean():+.4f}  {dd[~size].mean():+.4f}   "
          f"{int((ch > 0).sum())}/{len(ch)}   per clip {bc.round(3).to_dict()}")
# mechanism without the clip-wide scale case (0009) and the ambiguous lane row
lr = lambda s: np.log(s / gt)  # noqa: E731
keep = size & (vid != "simulation_0009") & ~q.str.contains("lane")
dim = q.map(dim_word)
for grp, m in (("length/width", keep & dim.isin(["length", "width"])), ("height", keep & (dim == "height"))):
    print(f"{grp:13s} n={int(m.sum())}: mean log shift aabb - hr_v1 {(lr(R['aabb']) - lr(R['hr_v1']))[m].mean():+.3f}; "
          f"score aabb {S['aabb'][m].mean():.3f} vs hr_v1 {S['hr_v1'][m].mean():.3f} "
          f"(hr_v2 {S['hr_v2'][m].mean():.3f}, opus {S['opus_v1'][m].mean():.3f})")
print("simulation_0009 boat length/width/height by run:",
      {k: R[k].loc[[1090, 1091, 1092]].tolist() for k in R}, "gt", gt.loc[[1090, 1091, 1092]].tolist())
