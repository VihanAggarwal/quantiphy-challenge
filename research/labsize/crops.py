"""Crops of named objects from Claude's boxes (test inputs only), for visual identification.

    .venv/bin/python research/labsize/crops.py captured_0013 ball [more video/object pairs ...]
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from common import ROOT, load_split, records  # noqa: E402

OUT = Path(sys.argv[0]).resolve().parent / "out"


def crops(video, obj, n=3, pad=1.5):
    df = load_split("test")
    path = df[df.video_id == video].video_path.iloc[0]
    rec = json.loads((ROOT / f"runs/test_v1_high_854/test/records/{video}.json").read_text())
    s = 1 / rec["meta"]["scale"]
    boxes = []
    for q in rec["parsed"]["questions"]:
        for tr in q.get("tracks", []):
            if obj.lower() in str(tr.get("object", "")).lower():
                for o in tr.get("obs", []):
                    b = o.get("box")
                    if b is None and o.get("extent"):
                        (x0, y0), (x1, y1) = o["extent"]
                        b = [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]
                    if b is None and o.get("point"):
                        x, y = o["point"]
                        b = [x - 15, y - 15, x + 15, y + 15]
                    if b:
                        boxes.append((o["frame"], b))
    boxes = sorted({f: b for f, b in boxes}.items())
    if not boxes:
        return None
    pick = [boxes[i] for i in np.linspace(0, len(boxes) - 1, min(n, len(boxes))).astype(int)]
    cap = cv2.VideoCapture(path)
    tiles = []
    for f, b in pick:
        cap.set(cv2.CAP_PROP_POS_FRAMES, f)
        ok, fr = cap.read()
        if not ok:
            continue
        x0, y0, x1, y1 = [v * s for v in b]
        cx, cy, h = (x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, y1 - y0, 20) * pad
        X0, Y0 = int(max(cx - h, 0)), int(max(cy - h, 0))
        X1, Y1 = int(min(cx + h, fr.shape[1])), int(min(cy + h, fr.shape[0]))
        c = fr[Y0:Y1, X0:X1]
        c = cv2.resize(c, (256, 256))
        cv2.putText(c, f"{video[9:]} {obj[:10]} f{f}", (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1)
        tiles.append(c)
    return np.hstack(tiles) if tiles else None


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    args = sys.argv[1:]
    name = args[0]
    rows = []
    for i in range(1, len(args), 2):
        c = crops(args[i], args[i + 1])
        if c is not None:
            if rows and c.shape[1] != rows[0].shape[1]:
                c = np.hstack([c, np.zeros((256, rows[0].shape[1] - c.shape[1], 3), np.uint8)]) \
                    if c.shape[1] < rows[0].shape[1] else c[:, :rows[0].shape[1]]
            rows.append(c)
    cv2.imwrite(str(OUT / f"{name}.jpg"), np.vstack(rows))
