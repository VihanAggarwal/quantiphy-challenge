"""Container fps / frame count vs dataset fps for every test video (test inputs only)."""
import sys
import cv2
import pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from common import *

df = load_split("test")
rows = []
for v, g in df.groupby("video_id"):
    cap = cv2.VideoCapture(g.video_path.iloc[0])
    rows.append(dict(video_id=v, fps=float(g.fps.iloc[0]), cfps=cap.get(cv2.CAP_PROP_FPS),
                     n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                     h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), cats=",".join(sorted(set(g.category))), nq=len(g)))
    cap.release()
r = pd.DataFrame(rows)
r.to_csv(ROOT / "research/d2static/out/fps_audit.csv", index=False)
x = r[(r.cfps - r.fps).abs() > 0.05]
pd.set_option("display.max_rows", 200); pd.set_option("display.width", 200)
print(len(x)); print(x.to_string(index=False))
