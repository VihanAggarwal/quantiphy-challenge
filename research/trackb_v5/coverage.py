import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import Data, src_of
D = Data()
t = D.test.copy(); t["src"] = t.video_id.map(src_of)
P = D.P["test"]
for m in ["cv_geo", "qwen_geo", "cvq_geo", "qwen_dense", "hybrid"]:
    t["own_" + m] = ~np.isclose(P[m].to_numpy(float), P["caw"].to_numpy(float), rtol=1e-6)
print(t.groupby(["category", "src"])[[c for c in t.columns if c.startswith("own_")]].mean().round(2).to_string())
print(t.groupby(["category", "src"]).size())
