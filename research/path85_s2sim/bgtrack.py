"""Moving-object masks by median-background subtraction (fixed Blender camera). Test inputs only.
    python bgtrack.py <video_id> [thr] -> out/bgtrack_<video_id>.csv (top components per frame)"""
import sys, cv2, numpy as np, pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent / "out"

def frames(vid):
    cap = cv2.VideoCapture(str(ROOT / "data/QuantiPhy" / f"{vid}.mp4")); fr = []
    while True:
        ok, img = cap.read()
        if not ok: break
        fr.append(img)
    return fr

def track(vid, thr=25, min_area=40, k=3):
    fr = frames(vid)
    bg = np.median(np.stack(fr[:: max(1, len(fr) // 40)]), axis=0).astype(np.int16)
    rows = []
    for i, img in enumerate(fr):
        d = np.abs(img.astype(np.int16) - bg).max(axis=2)
        m = (d > thr).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
        comps = sorted([(int(st[j, 4]), j) for j in range(1, n) if st[j, 4] >= min_area], reverse=True)[:k]
        rec = {"frame": i}
        for c, (a, j) in enumerate(comps):
            x, y, w, h = st[j, :4]
            rec.update({f"c{c}_area": a, f"c{c}_x0": x, f"c{c}_y0": y, f"c{c}_x1": x + w, f"c{c}_y1": y + h,
                        f"c{c}_cx": cen[j][0], f"c{c}_cy": cen[j][1]})
        rows.append(rec)
    return pd.DataFrame(rows)

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    v = sys.argv[1]; thr = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    d = track(v, thr)
    d.to_csv(OUT / f"bgtrack_{v}.csv", index=False)
    print(v, len(d))
