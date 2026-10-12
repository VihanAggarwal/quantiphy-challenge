"""Flat rectangular objects lying on the lab table (notebook, credit card): corners from a colour mask
(4-gon from the hull, refined by RANSAC lines on the mask contour), then metric sides two ways:
  plane  rays meet the table plane (orientation + scale from table_views anchors) lifted by the object's
         thickness;
  self   the object's own parallelogram rectification, scaled by its depth_info range at its centre.
Test inputs only."""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import rect  # noqa: E402
from corners import draw, fit_line, frame, intersect, ransac_line, refine, table_mask  # noqa: E402
from plane import C, anchor_scale  # noqa: E402
from table_views import VIEWS  # noqa: E402


def color_quad(fr, box, lo, hi):
    x0, y0, x1, y1 = box
    hsv = cv2.cvtColor(fr[y0:y1, x0:x1], cv2.COLOR_BGR2HSV)
    m = cv2.inRange(hsv, np.array(lo), np.array(hi))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    m = (lab == k).astype(np.uint8)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)
    hull = cv2.convexHull(c)
    per = cv2.arcLength(hull, True)
    q = None
    for eps in np.linspace(0.01, 0.1, 50):
        p = cv2.approxPolyDP(hull, eps * per, True)
        if len(p) == 4:
            q = p[:, 0, :].astype(float)
            break
    pts = c[:, 0, :].astype(float)
    # refine each edge by RANSAC on contour points near it (middle 70%)
    lines = []
    for i in range(4):
        a, b = q[i], q[(i + 1) % 4]
        d = b - a
        L = np.linalg.norm(d)
        u = d / L
        nn = np.array([-u[1], u[0]])
        s = (pts - a) @ u / L
        sel = pts[(s > 0.15) & (s < 0.85) & (np.abs((pts - a) @ nn) < 4)]
        lines.append(ransac_line(sel, thr=1.0)[0] if len(sel) >= 5 else fit_line(np.array([a, b])))
    cr = np.array([intersect(lines[(i - 1) % 4], lines[i]) for i in range(4)])
    return cr + [x0, y0], m


def plane_of(view, f):
    cfg = VIEWS[view]
    fr = frame(view)
    cr, _, _ = refine(fr, table_mask(fr), cfg["rough"], front=cfg["front"])
    X = rect.parallelogram(cr, f, C)
    n = np.cross(X[1] - X[0], X[3] - X[0])
    n /= np.linalg.norm(n)
    if n @ X[0] > 0:
        n = -n
    ss = []
    for name, (uv, r, h, R) in cfg["anchors"].items():
        if uv is None:
            uv = cr[3] if "FL" in name else cr[2]
        ss.append(anchor_scale(X, n, uv, r, f, h=h, R=R))
    s = float(np.median(ss))
    return n, s * (n @ X[0])  # plane: n.x = c (c < 0: camera side positive)


def sides_on_plane(cr, n, c, f, lift=0.0):
    d = rect.rays(cr, f, C)
    k = (c + lift) / (d @ n)
    P = d * k[:, None]
    return [float(np.linalg.norm(P[(i + 1) % 4] - P[i])) for i in range(4)], P


def sides_self(cr, f, r):
    X = rect.parallelogram(cr, f, C)
    ctr = X.mean(0)
    s = r / np.linalg.norm(ctr)
    X = X * s
    return [float(np.linalg.norm(X[(i + 1) % 4] - X[i])) for i in range(4)]
