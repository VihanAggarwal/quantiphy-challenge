import sys; sys.path.insert(0,'.')
import pandas as pd, numpy as np
from qp.data import load_split, load_validation
from qp import postprocess as pp
df = load_split("test")
v = load_validation()
vkeys = {(a, pp.norm_question(b)) for a, b in zip(v.video_id, v.question)}
df["overlap"] = [(a, pp.norm_question(b)) in vkeys for a, b in zip(df.video_id, df.question)]
best = pd.read_csv("submissions/trackA_cand_physb2_on_p21.csv").set_index("id")["parsed_value"]
run = pd.read_csv("runs/test_v1_high_854/test.csv").set_index("id")
df["pred"]=df.qid.map(best); df["geo"]=df.qid.map(run.geo_value); df["direct"]=df.qid.map(run.direct_value)
s = df[(df.video_source=="internet") & (df.category=="S2") & ~df.overlap].copy()
def kind(q):
    q=q.lower()
    if "acceler" in q: return "acc"
    if "veloc" in q or "speed" in q: return "vel"
    if "displacement" in q or "distance traveled" in q or "moving distance" in q: return "disp"
    return "size"
s["kind"]=s.question.map(kind)
s["lr"]=np.log(s.pred/s.direct)
print(s.groupby("kind").agg(n=("qid","size"), med_abs_lr=("lr", lambda x: np.median(np.abs(x))), frac_gt10=("lr", lambda x: np.mean(np.abs(x)>0.1))))
print("total scored S2 internet:", len(s))
x = s[np.abs(s.lr)>0.1].sort_values("lr")
pd.set_option("display.width",250); pd.set_option("display.max_colwidth",90)
print(x[["qid","video_id","kind","pred","direct","lr","question"]].to_string(index=False))
