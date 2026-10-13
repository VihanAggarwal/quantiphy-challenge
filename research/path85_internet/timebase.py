"""Internet clips + their segmented twins: dataset fps vs container fps, frame counts, duplicate-frame rate."""
import sys; sys.path.insert(0,'.')
import cv2, numpy as np, pandas as pd
from qp.data import load_split
df = load_split("test")
vids = sorted(v for v in df.video_id.unique() if v.startswith("internet"))
rows=[]
for v in vids:
    g = df[df.video_id==v]
    cap = cv2.VideoCapture(g.video_path.iloc[0]); n=int(cap.get(7)); cfps=cap.get(5)
    prev=None; d=[]; k=0
    while True:
        ok, im = cap.read()
        if not ok: break
        sm = cv2.resize(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), (160, 90)).astype(np.float32)
        if prev is not None: d.append(float(np.mean(np.abs(sm-prev))))
        prev = sm; k+=1
    d=np.array(d); dup = (d < 0.05*np.median(d[d>0])) if len(d) and (d>0).any() else d==0
    rows.append(dict(video=v, cat=g.category.iloc[0], dfps=g.fps.iloc[0], cfps=round(cfps,3), n=n, nread=k,
                     dur_d=round(k/g.fps.iloc[0],3), dur_c=round(k/cfps,3), dup_frac=round(float(dup.mean()),3) if len(d) else np.nan,
                     dup_idx=",".join(map(str, np.where(dup)[0][:12]+1))))
out = pd.DataFrame(rows)
pd.set_option("display.width",250); pd.set_option("display.max_rows",200)
print(out.to_string(index=False))
out.to_csv("research/path85_internet/out/timebase.csv", index=False)
