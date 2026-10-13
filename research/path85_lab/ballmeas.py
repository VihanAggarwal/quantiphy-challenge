"""Precise pixel diameters of lab balls (test inputs only): colour segmentation around Claude's box on a given frame,
ellipse fit -> minor / major axis in 1280-px units. Used to audit the lab focal length against stated sizes.
measure(video_id, frame, box1280, cls) -> dict(minor, major, cx, cy, area_d, ok)"""
import json, sys
from functools import lru_cache
from pathlib import Path
import cv2, numpy as np
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from qp.data import load_test

_VP = None


def vpath(v):
    global _VP
    if _VP is None:
        T = load_test(); _VP = T.drop_duplicates("video_id").set_index("video_id").video_path.to_dict()
    return _VP[v]


@lru_cache(maxsize=64)
def frame(v, n):
    cap = cv2.VideoCapture(vpath(v)); cap.set(cv2.CAP_PROP_POS_FRAMES, int(n)); ok, f = cap.read(); cap.release()
    return f if ok else None


def color_mask(hsv, bgr, cls):
    H, S, V = hsv[..., 0].astype(int), hsv[..., 1].astype(int), hsv[..., 2].astype(int)
    if cls == "tennis":
        return (H >= 22) & (H <= 48) & (S >= 70) & (V >= 70)
    if cls == "pingpong":
        return (S <= 50) & (V >= 150)
    if cls == "red":
        return ((H <= 8) | (H >= 168)) & (S >= 90) & (V >= 50)
    if cls == "basketball":
        return (H >= 3) & (H <= 22) & (S >= 90) & (V >= 50)
    if cls == "yoga":
        return (H >= 120) & (H <= 165) & (S >= 40)
    if cls == "soccer":   # white panels + black pentagons: bright-or-dark with low saturation
        return (S <= 60) & ((V >= 140) | (V <= 60))
    raise ValueError(cls)


def measure(v, n, box, cls, pad=1.0, debug_path=None):
    f = frame(v, n)
    if f is None:
        return dict(ok=False, why="noframe")
    Hh, Ww = f.shape[:2]
    x0, y0, x1, y1 = box
    cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
    s = max(w, h) * (1 + pad)
    X0, Y0 = int(max(0, cx - s)), int(max(0, cy - s)); X1, Y1 = int(min(Ww, cx + s)), int(min(Hh, cy + s))
    crop = f[Y0:Y1, X0:X1]
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    m = color_mask(hsv, crop, cls).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    nlab, lab, stats, cent = cv2.connectedComponentsWithStats(m)
    if nlab <= 1:
        return dict(ok=False, why="nomask")
    # component closest to the box centre among sizeable ones
    best, bd = None, 1e9
    for i in range(1, nlab):
        if stats[i, cv2.CC_STAT_AREA] < 0.15 * (min(w, h) / 2) ** 2 * np.pi:
            continue
        d = np.hypot(cent[i, 0] + X0 - cx, cent[i, 1] + Y0 - cy)
        if d < bd:
            best, bd = i, d
    if best is None:
        return dict(ok=False, why="small")
    comp = (lab == best).astype(np.uint8)
    cnts, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cnts, key=cv2.contourArea)
    if len(c) < 6:
        return dict(ok=False, why="contour")
    hull = cv2.convexHull(c)
    if len(hull) < 5:
        return dict(ok=False, why="hull")
    (ex, ey), (a1, a2), ang = cv2.fitEllipse(hull)
    area = cv2.contourArea(hull)
    out = dict(ok=True, minor=float(min(a1, a2)), major=float(max(a1, a2)), cx=float(ex + X0), cy=float(ey + Y0),
               area_d=float(2 * np.sqrt(area / np.pi)), touches=bool(comp[0].any() or comp[-1].any() or comp[:, 0].any() or comp[:, -1].any()),
               dist_box=float(bd), box_w=float(w))
    if debug_path:
        vis = crop.copy(); cv2.drawContours(vis, [hull], -1, (0, 0, 255), 1)
        cv2.imwrite(str(debug_path), cv2.resize(vis, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST))
    return out
