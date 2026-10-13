"""All segmented twins: dataset fps / container fps / frame counts vs their original; and whether the
submitted answer equals the original's answer (copied) or not."""
import sys; sys.path.insert(0,'.')
import cv2, numpy as np, pandas as pd
from qp.data import load_split
from qp import postprocess as pp
df = load_split("test")
best = pd.read_csv("submissions/trackA_cand_physb2_on_p21.csv").set_index("id")["parsed_value"]
df["pred"] = df.qid.map(best)
twins = sorted(v for v in df.video_id.unique() if v.endswith("_segmented"))
def info(v):
    p = df[df.video_id==v].video_path.iloc[0]
    cap = cv2.VideoCapture(p); return int(cap.get(7)), cap.get(5)
rows=[]
for t in twins:
    o = t.replace("_segmented","")
    gt = df[df.video_id==t]; go = df[df.video_id==o]
    nt, ct = info(t)
    if len(go): no, co = info(o); fo = go.fps.iloc[0]
    else: no, co, fo = np.nan, np.nan, np.nan
    # copied rows: same normalized question in original with same pred
    qo = {pp.norm_question(q): pr for q, pr in zip(go.question, go.pred)}
    copied = sum(1 for q, pr in zip(gt.question, gt.pred) if pp.norm_question(q) in qo and abs(qo[pp.norm_question(q)]/pr-1) < 1e-6)
    motion = sum(1 for q in gt.question if any(w in q.lower() for w in ("speed","veloc","acceler","displacement")))
    rows.append(dict(twin=t, cat=gt.category.iloc[0], n=len(gt), copied=copied, motion_q=motion, prior_same=(gt.prior.iloc[0].replace(" ","").lower()==go.prior.iloc[0].replace(" ","").lower()) if len(go) else None,
                     dfps_t=gt.fps.iloc[0], cfps_t=round(ct,2), n_t=nt, dfps_o=fo, cfps_o=round(co,2), n_o=no,
                     dur_t_d=round(nt/gt.fps.iloc[0],2), dur_t_c=round(nt/ct,2), dur_o_d=round(no/fo,2) if len(go) else np.nan))
out = pd.DataFrame(rows)
pd.set_option("display.width",250); pd.set_option("display.max_rows",300)
print(out.to_string(index=False))
out.to_csv("research/path85_internet/out/twin_fps.csv", index=False)
