"""How many simulation clips start with duplicated frames (frame 0 == frame 1)? Test inputs only."""
import cv2, numpy as np, pandas as pd, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp.data import load_test
t = load_test()
vids = sorted(set(t.video_id[t.video_source.isin(["simulation", "segmentation"])]))
rows = []
for v in vids:
    cap = cv2.VideoCapture(str(ROOT / "data/QuantiPhy" / f"{v}.mp4"))
    fr = []
    for i in range(4):
        ok, img = cap.read()
        if not ok: break
        fr.append(cv2.resize(img, (320, 180)).astype(float))
    d = [np.abs(fr[i + 1] - fr[i]).mean() for i in range(len(fr) - 1)]
    rows.append(dict(video_id=v, d01=d[0], d12=d[1] if len(d) > 1 else np.nan, d23=d[2] if len(d) > 2 else np.nan))
r = pd.DataFrame(rows)
r["dup01"] = (r.d01 < 0.2 * r[["d12", "d23"]].max(axis=1)) & (r.d12 > 0.3)
r.to_csv(Path(__file__).parent / "out_dupcheck.csv", index=False)
print(len(r), "dup first frame:", int(r.dup01.sum()))
print(r[r.dup01].video_id.tolist()[:80])
