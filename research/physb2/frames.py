"""Contact sheet of raw frames (frame index + time stamped) for visual family checks.
    .venv/bin/python research/physb2/frames.py internet_0055 [n_frames] [out.jpg]
"""
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
vid = sys.argv[1]
nf = int(sys.argv[2]) if len(sys.argv) > 2 else 6
out = sys.argv[3] if len(sys.argv) > 3 else str(ROOT / f"research/physb2/out/sheets/{vid}.jpg")
Path(out).parent.mkdir(parents=True, exist_ok=True)  # sheets are not committed (15 MB); regenerate
cap = cv2.VideoCapture(str(ROOT / f"data/QuantiPhy/{vid}.mp4"))
n, fps = int(cap.get(7)), cap.get(5)
tiles = []
for fi in np.linspace(0, n - 1, nf).astype(int):
    cap.set(1, fi)
    ok, im = cap.read()
    if not ok:
        continue
    h, w = im.shape[:2]
    k = 640 / max(h, w)
    im = cv2.resize(im, (int(w * k), int(h * k)))
    cv2.putText(im, f"{fi} t={fi / fps:.2f}", (10, 30), 0, 0.9, (0, 255, 255), 2)
    tiles.append(im)
h = max(t.shape[0] for t in tiles); w = max(t.shape[1] for t in tiles)
tiles = [cv2.copyMakeBorder(t, 0, h - t.shape[0], 0, w - t.shape[1], 0) for t in tiles]
rows = [np.hstack(tiles[i:i + 3] + [np.zeros_like(tiles[0])] * (3 - len(tiles[i:i + 3]))) for i in range(0, len(tiles), 3)]
cv2.imwrite(out, np.vstack(rows))
print(vid, "frames", n, "fps", fps, "size", w, h, "->", out)
