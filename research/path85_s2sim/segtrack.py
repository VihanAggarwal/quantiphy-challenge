"""Per-frame mask tracks from segmented twins (plain white background): bbox and centroid per frame.
    python segtrack.py <video_id> [...]   -> out/segtrack_<video_id>.csv
Only test INPUT videos are read."""
from __future__ import annotations
import sys
from pathlib import Path
import cv2, numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent / "out"

def track(vid: str, thr: int = 235, min_area: int = 30) -> pd.DataFrame:
    cap = cv2.VideoCapture(str(ROOT / "data/QuantiPhy" / f"{vid}.mp4"))
    rows = []
    i = 0
    while True:
        ok, img = cap.read()
        if not ok:
            break
        g = img.min(axis=2)
        m = (g < thr).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
        comps = [(st[k, 4], k) for k in range(1, n) if st[k, 4] >= min_area]
        comps.sort(reverse=True)
        rec = {"frame": i, "ncomp": len(comps)}
        for j, (a, k) in enumerate(comps[:4]):
            x, y, w, h = st[k, :4]
            ys, xs = np.nonzero(lab == k)
            rec.update({f"c{j}_area": a, f"c{j}_x0": x, f"c{j}_y0": y, f"c{j}_x1": x + w, f"c{j}_y1": y + h,
                        f"c{j}_cx": xs.mean(), f"c{j}_cy": ys.mean()})
        # union of all components
        if comps:
            ys, xs = np.nonzero(m)
            rec.update({"u_x0": xs.min(), "u_x1": xs.max() + 1, "u_y0": ys.min(), "u_y1": ys.max() + 1,
                        "u_cx": xs.mean(), "u_cy": ys.mean(), "u_area": len(xs)})
        rows.append(rec)
        i += 1
    return pd.DataFrame(rows)

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for v in sys.argv[1:]:
        d = track(v)
        d.to_csv(OUT / f"segtrack_{v}.csv", index=False)
        print(v, len(d), d.ncomp.value_counts().to_dict())
