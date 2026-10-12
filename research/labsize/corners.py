"""Table-top corners from the uniform-background lab renders (captured_XXXXx / s): mask of non-background
pixels, the table component, its outer contour simplified to a polygon; the top face is the quadrilateral of
the two back corners and the two front corners where the front band's short vertical sides start.
Every result is drawn for an eye check (out/corners_<video>.png). Test inputs only."""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from common import load_split  # noqa: E402

OUT = Path(__file__).parent / "out"


def frame(video, idx=0):
    df = load_split("test")
    p = df[df.video_id == video].video_path.iloc[0]
    cap = cv2.VideoCapture(p)
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ok, fr = cap.read()
    return fr


def table_mask(fr, thr=40, wood_only=False):
    h, w = fr.shape[:2]
    corners = np.array([fr[5, 5], fr[5, w - 5], fr[h // 2, 5], fr[h // 2, w - 5]], float)
    bg = np.median(corners, axis=0)
    d = np.abs(fr.astype(float) - bg).sum(axis=2)
    m = (d > thr).astype(np.uint8)
    hsv = cv2.cvtColor(fr, cv2.COLOR_BGR2HSV)
    wood = ((hsv[..., 0] >= 5) & (hsv[..., 0] <= 25) & (hsv[..., 1] >= 60) & (hsv[..., 2] >= 40)).astype(np.uint8)
    if wood_only:
        m = m & wood
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    return (lab == k).astype(np.uint8)


def polygon(mask, n=6):
    cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)
    hull = cv2.convexHull(c)
    per = cv2.arcLength(hull, True)
    for eps in np.linspace(0.002, 0.05, 60):
        p = cv2.approxPolyDP(hull, eps * per, True)
        if len(p) <= n:
            return p[:, 0, :].astype(float)
    return p[:, 0, :].astype(float)


def draw(fr, polys, name):
    im = fr.copy()
    for poly, col in polys:
        p = np.round(poly).astype(int)
        cv2.polylines(im, [p], True, col, 1)
        for i, q in enumerate(p):
            cv2.circle(im, tuple(q), 3, col, -1)
            cv2.putText(im, str(i), tuple(q + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, col, 1)
    cv2.imwrite(str(OUT / f"corners_{name}.png"), im)


if __name__ == "__main__":
    for v in sys.argv[1:]:
        fr = frame(v)
        m = table_mask(fr)
        p = polygon(m)
        print(v, np.round(p).astype(int).tolist())
        draw(fr, [(p, (0, 0, 255))], v)


def fit_line(pts):
    """Total-least-squares line through pts: (point, unit direction)."""
    pts = np.asarray(pts, float)
    m = pts.mean(0)
    _, _, vt = np.linalg.svd(pts - m)
    return m, vt[0]


def intersect(l1, l2):
    (p, d), (q, e) = l1, l2
    A = np.column_stack([d, -e])
    t = np.linalg.solve(A, q - p)
    return p + t[0] * d


def contour_pts(mask):
    cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return max(cs, key=cv2.contourArea)[:, 0, :].astype(float)


def edge_points(cpts, a, b, keep=(0.2, 0.8), tol=6.0):
    """Contour points near the segment a-b, within its middle `keep` fraction."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = b - a
    L = np.linalg.norm(d)
    u = d / L
    nrm = np.array([-u[1], u[0]])
    s = (cpts - a) @ u / L
    off = np.abs((cpts - a) @ nrm)
    return cpts[(s > keep[0]) & (s < keep[1]) & (off < tol)]


def front_top_points(fr, mask, a, b, max_up=60, keep=(0.15, 0.85)):
    """Points of the top-face / front-band boundary between rough front-top corners a, b: per column, the
    strongest downward luminance drop within max_up px above the mask's bottom boundary."""
    g = cv2.GaussianBlur(cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY).astype(float), (3, 3), 0)
    a, b = np.asarray(a, float), np.asarray(b, float)
    out = []
    for s in np.linspace(keep[0], keep[1], 80):
        x0, y0 = a + s * (b - a)
        x = int(round(x0))
        col = mask[:, x]
        ys = np.where(col > 0)[0]
        if not len(ys):
            continue
        ybot = ys[ys >= y0 - 5].max() if (ys >= y0 - 5).any() else None
        if ybot is None:
            continue
        lo, hi = int(max(y0 - 25, 1)), int(min(y0 + 25, ybot - 2))
        if hi <= lo + 2:
            continue
        gy = g[lo + 1:hi + 1, x] - g[lo - 1:hi - 1, x]
        out.append((x, lo + int(np.argmin(gy))))
    return np.array(out, float)


def ransac_line(pts, thr=1.5, iters=300, seed=0):
    rng = np.random.default_rng(seed)
    pts = np.asarray(pts, float)
    best = None
    for _ in range(iters):
        i, j = rng.choice(len(pts), 2, replace=False)
        d = pts[j] - pts[i]
        if np.linalg.norm(d) < 5:
            continue
        n = np.array([-d[1], d[0]]) / np.linalg.norm(d)
        inl = np.abs((pts - pts[i]) @ n) < thr
        if best is None or inl.sum() > best.sum():
            best = inl
    return fit_line(pts[best]), int(best.sum()), len(pts)


def refine(fr, mask, rough, front=(), tol=15.0, keep=(0.1, 0.9)):
    """Corners as intersections of RANSAC lines fitted to each edge's points. rough: 4 corners in order;
    front: indices i of edges rough[i] -> rough[i+1] that are a top/band boundary (no contour there: the
    luminance drop is used). Returns corners, lines, (inliers, points) per edge."""
    cpts = contour_pts(mask)
    lines, stats = [], []
    if isinstance(front, int):
        front = (front,)
    for i in range(4):
        a, b = rough[i], rough[(i + 1) % 4]
        pts = front_top_points(fr, mask, a, b) if i in front else edge_points(cpts, a, b, keep=keep, tol=tol)
        if len(pts) < 5:
            raise ValueError(f"edge {i}: {len(pts)} points")
        ln, ni, n = ransac_line(pts)
        lines.append(ln)
        stats.append((ni, n))
    return np.array([intersect(lines[(i - 1) % 4], lines[i]) for i in range(4)]), lines, stats
