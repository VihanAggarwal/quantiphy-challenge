"""Identical-camera sibling pairs among 2D simulation clips (|id gap| <= 3): median background (every 3rd frame,
160 px wide) NCC >= 0.97. Test input videos only. -> out/samecam.csv"""
import itertools, re, sys
from pathlib import Path
import cv2, numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp.data import load_test
t = load_test()
two = t[t.video_source.eq("simulation") & t.video_type.str[1].eq("2")]
vids = sorted(set(two.video_id))
def bg(v):
    cap = cv2.VideoCapture(str(ROOT / "data/QuantiPhy" / f"{v}.mp4")); fr = []; i = 0
    while True:
        ok, f = cap.read()
        if not ok: break
        if i % 3 == 0:
            fr.append(cv2.cvtColor(cv2.resize(f, (160, int(160 * f.shape[0] / f.shape[1]))), cv2.COLOR_BGR2GRAY).astype(np.float32))
        i += 1
    return np.median(np.stack(fr), axis=0)
B = {v: bg(v) for v in vids}
num = lambda v: int(re.search(r"(\d+)", v).group(1))
rows = []
for a, b in itertools.combinations(vids, 2):
    if abs(num(a) - num(b)) > 3 or B[a].shape != B[b].shape: continue
    x, y = B[a].ravel() - B[a].mean(), B[b].ravel() - B[b].mean()
    ncc = float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y) + 1e-9))
    rows.append(dict(a=a, b=b, ncc=ncc))
d = pd.DataFrame(rows)
d.to_csv(Path(__file__).parent / "out/samecam.csv", index=False)
pr = two.drop_duplicates("video_id").set_index("video_id").prior
x = d[d.ncc >= 0.97].assign(pa=lambda z: z.a.map(pr), pb=lambda z: z.b.map(pr))
x = x[x.pa.str.lower() != x.pb.str.lower()]
pd.set_option("display.width", 220); pd.set_option("display.max_colwidth", 60); pd.set_option("display.max_rows", 200)
print(len(d), "pairs;", int((d.ncc >= 0.97).sum()), "same camera;", len(x), "with different priors")
print(x.round(3).to_string())
