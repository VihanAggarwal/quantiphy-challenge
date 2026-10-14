"""Track B vs Track A on 2D test rows: is B's error clip-level (prior scale) or row-level (target)?
Proxy only (A is not a label). Usage: .venv/bin/python research/r86/trackb_opt/diag_2d.py"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from qp.data import load_split
RUN = Path("/tmp/claude-0/tb3/x/trackb_v1/test")
df = load_split("test").reset_index(drop=True)
A = pd.read_csv(ROOT / "submissions/trackA_combo3_on_combo2.csv")
A = A.rename(columns={A.columns[0]: "qid"}).set_index("qid")["parsed_value"]
rawA = pd.read_csv(ROOT / "runs/test_v1_high_854/test.csv").set_index("id")
def rd(p):
    d = pd.read_csv(p); return d.set_index(d.columns[0])
Bq = rd(RUN / "qwen/geometry.csv"); Bc = rd(RUN / "cvq/geometry.csv"); Bcv = rd(RUN / "cv/geometry.csv")
V3 = pd.read_csv(ROOT / "submissions/trackB_v3_catmedian_famrules.csv"); V3 = V3.set_index(V3.columns[0])["parsed_value"]
df["cat"] = df.category if "category" in df else df.inference_type.str[0] + np.where(df.video_type.str.contains("3"), "3", "2")
df["src"] = df.video_id.str.split("_").str[0]
q = df.question.str.lower()
df["tk"] = np.select([q.str.contains("acceler"), q.str.contains("veloc|speed"), q.str.contains("travel|distance|far|apart")], ["accel", "speed", "dist"], "size")
qid = df.qid
for name, s in [("rawA_geo", rawA.geo_value), ("qwen_geo", Bq.geo_value), ("cvq_geo", Bc.geo_value), ("cv_geo", Bcv.geo_value), ("v3", V3)]:
    df[name] = pd.to_numeric(s.reindex(qid).to_numpy(), errors="coerce")
df["A"] = A.reindex(qid).to_numpy()
two = df[df.cat.isin(["S2", "D2"])].copy()
for m in ["qwen_geo", "cvq_geo", "v3"]:
    lr = np.log(two[m] / two.rawA_geo)
    two["lr"] = lr
    g = two.dropna(subset=["lr"])
    clip = g.groupby("video_id").lr.transform("median")
    res = g.lr - clip
    print(f"\n== {m} vs Claude raw geometry, 2D rows n={len(g)}")
    print(" gross |lr|>ln1.5:", round((g.lr.abs() > np.log(1.5)).mean(), 3),
          " clip-median gross:", round((clip.abs() > np.log(1.5)).mean(), 3),
          " within-clip residual gross:", round((res.abs() > np.log(1.5)).mean(), 3))
    t = g.assign(gross=g.lr.abs() > np.log(1.5), cgross=clip.abs() > np.log(1.5), rgross=res.abs() > np.log(1.5))
    print(t.groupby(["cat", "src", "tk"])[["gross", "cgross", "rgross"]].mean().round(2).assign(n=t.groupby(["cat", "src", "tk"]).size()).to_string())
