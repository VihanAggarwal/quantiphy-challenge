"""For every lab test clip: clip duration vs the times the questions ask about (test inputs only)."""
import re, sys
import cv2
sys.path.insert(0, '/home/user/quantiphy-challenge')
from qp.data import load_split
df = load_split('test')
lab = df[df.video_id.str.startswith('captured_')]
rows = []
for vid, g in lab.groupby('video_id'):
    p = g.video_path.iloc[0]
    cap = cv2.VideoCapture(p); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps = cap.get(cv2.CAP_PROP_FPS); cap.release()
    ts = []
    for q in list(g.question) + list(g.depth_info) + list(g.prior):
        ts += [float(x) for x in re.findall(r'(\d+(?:\.\d+)?)\s*s\b', q)]
    dur = n / fps if fps else 0
    rows.append((vid, n, fps, dur, max(ts) if ts else None, sorted(set(ts))))
for r in rows:
    flag = '  <-- beyond' if r[4] and r[4] > r[3] else ''
    print(f"{r[0]:18s} n={r[1]:4d} fps={r[2]:.2f} dur={r[3]:.2f}s maxT={r[4]} {r[5][:12]}{flag}")
