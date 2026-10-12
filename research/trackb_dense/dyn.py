"""(Copied from research/levers_2026-10-11/levers_scripts_reports.tar.gz dynprior/dyn.py.)
Rigid-aware dense tracking of a 2D clip's motion-prior object (CPU, OpenCV only).

Per video:
  * frames decoded once, grey, long side <= WORK_SIDE (work px; results mapped back to original px)
  * median background over sampled frames; static-camera share of changed pixels (as qp.refine)
  * anchor: a box of the prior object at the frame nearest the middle of Claude's prior track
    (the prior track's own box, else a same-name box from another track that frames the prior point,
     else the foreground component under the point (static camera), else a LoG blob box)
  * KLT: Shi-Tomasi corners in the anchor box (foreground pixels only when the camera is static),
    tracked frame to frame forward and backward with a forward-backward check; per frame a
    similarity transform anchor->frame (RANSAC) moves the canonical reference point (anchor box
    centre). Features carry a random half label: two independent half-set trajectories.
    Lost features are re-seeded inside the transformed box (their anchor coordinates via the inverse).
  * MASK (static camera only): foreground component overlapping the predicted box -> centroid.
"""
from __future__ import annotations

import math

import cv2
import numpy as np

WORK_SIDE = 960
FB_MAX = 0.7           # work px forward-backward error
MIN_FEAT = 5
RANSAC_THR = 1.5       # work px
CHANGE_GREY = 14
STATIC_MAX = 0.15


def load_grey(path: str, work_side: int = WORK_SIDE, max_bytes: float = 7e8):
    cap = cv2.VideoCapture(path)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 300
    W0, H0 = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    if work_side is None and W0 > 0:
        work_side = max(W0, H0) * min(1.0, math.sqrt(max_bytes / (n * W0 * H0)))
    frames = []
    s = None
    while True:
        ok, img = cap.read()
        if not ok:
            break
        if s is None:
            H, W = img.shape[:2]
            s = min(1.0, work_side / max(H, W))
            size = (int(round(W * s)), int(round(H * s)))
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if s < 1:
            g = cv2.resize(g, size, interpolation=cv2.INTER_AREA)
        frames.append(g)
    cap.release()
    return np.array(frames), (s or 1.0)


def background(G: np.ndarray, n: int = 40):
    idx = np.unique(np.linspace(0, len(G) - 1, min(n, len(G))).round().astype(int))
    bg = np.median(G[idx], axis=0).astype(np.uint8)
    share = [float((cv2.absdiff(G[i], bg) > 12).mean()) for i in idx]
    return bg, float(np.median(share))


def fg_mask(g, bg, thr=CHANGE_GREY):
    m = (cv2.absdiff(g, bg) > thr).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return m


def component_box(mask, point, box=None):
    """Box (x0,y0,x1,y1) and centroid of the fg component containing / nearest the point (within box)."""
    n, lab, stats, cents = cv2.connectedComponentsWithStats(mask, 8)
    if n <= 1:
        return None
    x, y = int(round(point[0])), int(round(point[1]))
    H, W = mask.shape
    best, bd = None, 1e18
    for k in range(1, n):
        x0, y0, w, h, a = stats[k]
        if a < 12:
            continue
        if box is not None:
            ix = min(x0 + w, box[2]) - max(x0, box[0])
            iy = min(y0 + h, box[3]) - max(y0, box[1])
            if ix <= 0 or iy <= 0:
                continue
        if 0 <= x < W and 0 <= y < H and lab[y, x] == k:
            d = 0
        else:
            d = math.hypot(cents[k][0] - x, cents[k][1] - y)
        if d < bd:
            best, bd = k, d
    if best is None:
        return None
    x0, y0, w, h, a = stats[best]
    return (x0, y0, x0 + w, y0 + h), tuple(cents[best]), int(a), lab == best


def _detect(g, box, fg=None, maxc=200):
    H, W = g.shape
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if x1 - x0 < 4 or y1 - y0 < 4:
        return np.zeros((0, 2), np.float32)
    m = np.zeros_like(g)
    m[y0:y1, x0:x1] = 255
    if fg is not None:
        fgd = cv2.dilate(fg, np.ones((3, 3), np.uint8))
        m2 = m & (fgd * 255)
        if m2.sum() / 255 > 30:
            m = m2
    md = max(2, int(min(x1 - x0, y1 - y0) / 20))
    p = cv2.goodFeaturesToTrack(g, maxCorners=maxc, qualityLevel=0.005, minDistance=md, mask=m, blockSize=5)
    return np.zeros((0, 2), np.float32) if p is None else p.reshape(-1, 2).astype(np.float32)


LK = dict(winSize=(21, 21), maxLevel=3, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))


def _lk(g0, g1, p0):
    if not len(p0):
        return p0, np.zeros(0, bool)
    p1, st, _ = cv2.calcOpticalFlowPyrLK(g0, g1, p0.reshape(-1, 1, 2), None, **LK)
    pb, st2, _ = cv2.calcOpticalFlowPyrLK(g1, g0, p1, None, **LK)
    fb = np.linalg.norm(pb.reshape(-1, 2) - p0, axis=1)
    ok = (st.ravel() == 1) & (st2.ravel() == 1) & (fb < FB_MAX)
    return p1.reshape(-1, 2), ok


def _sim(A, B):
    """Similarity A->B (2x3) by RANSAC, inlier mask."""
    if len(A) < 3:
        return None, None
    M, inl = cv2.estimateAffinePartial2D(A, B, method=cv2.RANSAC, ransacReprojThreshold=RANSAC_THR,
                                         maxIters=500, confidence=0.99)
    if M is None:
        return None, None
    return M, inl.ravel().astype(bool)


def klt_rigid(G, a, box, fgs=None, seed=0):
    """Reference-point trajectories (all features, half 0, half 1) in work px, nan where lost."""
    rng = np.random.default_rng(seed)
    N = len(G)
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    corners = np.array([[box[0], box[1]], [box[2], box[1]], [box[2], box[3]], [box[0], box[3]]], np.float32)
    out = {k: np.full((N, 2), np.nan) for k in ("all", "h0", "h1")}
    info = {"n_inl": np.zeros(N, int), "scale": np.full(N, np.nan), "rot": np.full(N, np.nan),
            "res": np.full(N, np.nan)}
    p_a = _detect(G[a], box, None if fgs is None else fgs(a))
    if len(p_a) < MIN_FEAT:
        return None, info
    lab = rng.integers(0, 2, len(p_a))
    for k in out:
        out[k][a] = (cx, cy)
    info["n_inl"][a] = len(p_a)
    info["scale"][a] = 1.0
    info["rot"][a] = 0.0
    for step in (1, -1):
        anc = p_a.copy()
        cur = p_a.copy()
        hl = lab.copy()
        M_prev = np.array([[1, 0, 0], [0, 1, 0]], float)
        f = a
        while 0 <= f + step < N:
            g0, g1 = G[f], G[f + step]
            nxt, ok = _lk(g0, g1, cur)
            anc, cur, hl = anc[ok], nxt[ok], hl[ok]
            M, inl = _sim(anc, cur)
            if M is None or inl.sum() < MIN_FEAT:
                break
            anc, cur, hl = anc[inl], cur[inl], hl[inl]
            f += step
            ref = M @ np.array([cx, cy, 1.0])
            out["all"][f] = ref
            for h in (0, 1):
                sel = hl == h
                if sel.sum() >= 4:
                    Mh, _ = _sim(anc[sel], cur[sel])
                    if Mh is not None:
                        out[f"h{h}"][f] = Mh @ np.array([cx, cy, 1.0])
            info["n_inl"][f] = len(anc)
            sc = math.hypot(M[0, 0], M[1, 0])
            info["scale"][f] = sc
            info["rot"][f] = math.degrees(math.atan2(M[1, 0], M[0, 0]))
            pred = anc @ M[:, :2].T + M[:, 2]
            info["res"][f] = float(np.sqrt(np.mean(np.sum((pred - cur) ** 2, 1))))
            M_prev = M
            # re-seed when the set thins out
            if len(anc) < max(2 * MIN_FEAT, 0.5 * len(p_a)):
                bx = corners @ M[:, :2].T + M[:, 2]
                nb = (bx[:, 0].min(), bx[:, 1].min(), bx[:, 0].max(), bx[:, 1].max())
                newp = _detect(G[f], nb, None if fgs is None else fgs(f))
                if len(newp):
                    d = np.min(np.linalg.norm(newp[:, None] - cur[None], axis=2), axis=1) if len(cur) else np.full(len(newp), 99)
                    newp = newp[d > 2]
                if len(newp):
                    A = M[:, :2]
                    Ai = np.linalg.inv(A)
                    newa = (newp - M[:, 2]) @ Ai.T
                    anc = np.vstack([anc, newa.astype(np.float32)])
                    cur = np.vstack([cur, newp])
                    hl = np.r_[hl, rng.integers(0, 2, len(newp))]
    return out, info


def mask_track(G, bg, a, point, box, thr=CHANGE_GREY):
    """Foreground-component centroid per frame, followed from the anchor (box overlap)."""
    N = len(G)
    cen = np.full((N, 2), np.nan)
    area = np.full(N, np.nan)
    boxes = np.full((N, 4), np.nan)
    m = fg_mask(G[a], bg, thr)
    got = component_box(m, point, box)
    if got is None:
        return None
    b, c, ar, _ = got
    cen[a], area[a], boxes[a] = c, ar, b
    for step in (1, -1):
        pb, pc, par = b, np.array(c), ar
        vel = np.zeros(2)
        f = a
        while 0 <= f + step < N:
            f += step
            mm = fg_mask(G[f], bg, thr)
            pad = 0.25 * max(pb[2] - pb[0], pb[3] - pb[1]) + 4
            pred = pc + vel
            sb = (pb[0] + vel[0] - pad, pb[1] + vel[1] - pad, pb[2] + vel[0] + pad, pb[3] + vel[1] + pad)
            g2 = component_box(mm, pred, sb)
            if g2 is None:
                break
            nb, nc, nar, _ = g2
            if not (0.6 * par <= nar <= 1.6 * par):
                break
            nc = np.array(nc)
            vel = nc - pc
            pb, pc, par = nb, nc, nar
            cen[f], area[f], boxes[f] = nc, nar, nb
    return {"cen": cen, "area": area, "box": boxes}


def seg_track(G, bg, a, point, box, thr=10, jump=1.8):
    """White-background (segmented) clip: foreground component followed from the anchor without
    stopping on area changes (articulated movers); frames whose area jumps > `jump` x the running
    median (merge with another object / partial exit) are marked invalid but tracking continues
    from the prediction. Returns centroid, box and a valid flag per frame."""
    N = len(G)
    cen = np.full((N, 2), np.nan)
    boxes = np.full((N, 4), np.nan)
    area = np.full(N, np.nan)
    valid = np.zeros(N, bool)
    got = component_box(fg_mask(G[a], bg, thr), point, box)
    if got is None:
        return None
    b, c, ar, _ = got
    cen[a], boxes[a], area[a], valid[a] = c, b, ar, True
    for step in (1, -1):
        pb, pc = np.array(b, float), np.array(c, float)
        vel = np.zeros(2)
        hist = [ar]
        f = a
        miss = 0
        while 0 <= f + step < N:
            f += step
            mm = fg_mask(G[f], bg, thr)
            pad = 0.3 * max(pb[2] - pb[0], pb[3] - pb[1]) + 4
            pred = pc + vel
            sb = (pb[0] + vel[0] - pad, pb[1] + vel[1] - pad, pb[2] + vel[0] + pad, pb[3] + vel[1] + pad)
            g2 = component_box(mm, pred, sb)
            if g2 is None:
                miss += 1
                if miss > 3:
                    break
                pc = pc + vel
                pb = pb + np.r_[vel, vel]
                continue
            nb, nc, nar, _ = g2
            nc = np.array(nc, float)
            med = float(np.median(hist[-9:]))
            ok = (1 / jump) * med <= nar <= jump * med
            if ok:
                miss = 0
                vel = nc - pc if np.isfinite(nc).all() else vel
                pb, pc = np.array(nb, float), nc
                hist.append(nar)
                cen[f], boxes[f], area[f], valid[f] = nc, nb, nar, True
            else:
                miss += 1
                if miss > 6:
                    break
                pc = pc + vel
                pb = pb + np.r_[vel, vel]
    return {"cen": cen, "box": boxes, "area": area, "valid": valid}
