"""Sensitivity of D2 timed answers in duplicated-first-frame clips to a one-frame time offset (t -> t + 1/fps):
geometry re-solved on the replayed annotations (no API). Test inputs only."""
import pickle, sys
from dataclasses import replace
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from qp.geometry import solve
from qp.data import load_test
rp = pickle.load(open(ROOT / "research/path85_s2sim/out/replay_s2.pkl", "rb"))
t = load_test().set_index("qid")
dup = pd.read_csv(ROOT / "research/path85_s2sim/out_dupcheck.csv").set_index("video_id").dup01
rows = []
for q, o in rp.items():
    sp = o["spec"]
    if t.category[q] not in ("D2", "S2") or sp.target.time is None or o["value"] is None: continue
    if sp.target.kind not in ("speed", "acceleration", "distance", "displacement"): continue
    s2 = replace(sp, target=replace(sp.target, time=float(sp.target.time + 1 / o["fps"])))
    a = solve(s2, o["tracks"], o["image_size"], o["fps"], seen_scale=o["seen"])
    rows.append(dict(qid=q, video_id=o["video_id"], cat=t.category[q], kind=sp.target.kind, t=sp.target.time,
                     dup=bool(dup.get(o["video_id"], False)), geo=o["value"], shifted=a.value))
d = pd.DataFrame(rows); d["ratio"] = d.shifted / d.geo
d.to_csv(HERE / "out/dupshift.csv", index=False)
g = d.groupby(["cat", "dup", "kind"]).ratio.agg(["size", lambda s: np.nanmedian(np.abs(np.log(s))), lambda s: (np.abs(np.log(s)) > 0.05).sum()])
print(g)
