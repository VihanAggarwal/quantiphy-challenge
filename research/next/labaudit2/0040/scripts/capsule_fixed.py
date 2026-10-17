"""Constrained capsule fit (fixed axis angle, half-length and radius taken from clean neighbour frames; only the
centre is free) on occluded frames. Also draws the fitted capsule for visual checking."""
import cv2, numpy as np, json, sys
exec(open('/home/user/quantiphy-challenge/research/next/labaudit2/0040/scripts/track_capsule.py').read().split("out = {}")[0])
def seg_dist(p, c, th, L):
    d = np.array([np.cos(th), np.sin(th)]); q = p - c
    s = np.clip(q @ d, -L, L); return np.linalg.norm(q - s[:, None] * d, axis=1)
def edges(i):
    d = np.abs(A[i] - med).max(-1); gimg = cv2.cvtColor(fr[i], cv2.COLOR_BGR2GRAY)
    m = ((d > 35) & (gimg > 120)).astype(np.uint8); m[690:] = 0
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m); k = 1 + np.argmax(st[1:, 4]); M = lab == k
    Mu = M.astype(np.uint8); bd = (Mu - cv2.erode(Mu, np.ones((3, 3), np.uint8))).astype(bool)
    dil_bg = cv2.dilate((bg & ~M).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    obj_near = cv2.dilate((~bg & ~M).astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
    by, bx = np.nonzero(bd & dil_bg & ~obj_near); return np.c_[bx, by].astype(float), M
spec = {32: [(49, 17.5, 18.5), (45, 19, 18.5), (52, 15, 18.0)],
        34: [(131, 13, 18.5), (128, 15, 18.5), (135, 11, 19.0), (131, 13, 17.5)],
        35: [(133, 12.4, 19.8), (131, 13, 18.5), (135, 14, 18.5)],
        38: [(36, 16, 18.5), (33, 15, 18.0), (40, 17, 19.0)],
        36: [(172.9, 13.6, 17.4)], 37: [(12.2, 14.0, 17.1)]}
res = {}
for i, lst in spec.items():
    P, M = edges(i)
    ys, xs = np.nonzero(M); c0 = np.array([xs.mean(), ys.mean()])
    for th, L, r in lst:
        c = c0.copy(); t = np.radians(th)
        for _ in range(100):   # Gauss-Newton on the centre, Cauchy weights
            f = seg_dist(P, c, t, L) - r; w = 1 / (1 + (f / 1.5) ** 2)
            J = np.zeros((len(P), 2))
            for j in range(2):
                cp = c.copy(); cp[j] += 1e-3; J[:, j] = (seg_dist(P, cp, t, L) - r - f) / 1e-3
            dc = np.linalg.solve((J * w[:, None]).T @ J + 1e-6 * np.eye(2), -(J * w[:, None]).T @ f)
            c += dc
            if np.abs(dc).max() < 1e-4: break
        f = seg_dist(P, c, t, L) - r
        print(f'f{i} th={th} L={L} r={r}: centre ({c[0]:.1f},{c[1]:.1f})  centroid ({c0[0]:.1f},{c0[1]:.1f})  n={len(P)} rms={np.sqrt(np.mean(np.minimum(f**2, 25))):.2f}')
        res.setdefault(i, []).append([c[0], c[1]])
    # drawing for the first spec
    th, L, r = lst[0]; c = np.array(res[i][0]); t = np.radians(th); d = np.array([np.cos(t), np.sin(t)])
    im = fr[i].copy()
    for p in P.astype(int): im[p[1], p[0]] = (0, 255, 0)
    a, b = c - L * d, c + L * d
    cv2.circle(im, tuple(np.round(a).astype(int)), int(round(r)), (0, 0, 255), 1)
    cv2.circle(im, tuple(np.round(b).astype(int)), int(round(r)), (0, 0, 255), 1)
    cv2.drawMarker(im, tuple(np.round(c).astype(int)), (0, 0, 255), cv2.MARKER_CROSS, 8, 1)
    cv2.drawMarker(im, tuple(np.round(c0).astype(int)), (255, 0, 255), cv2.MARKER_TILTED_CROSS, 8, 1)
    x0, y0 = int(c[0]) - 60, int(c[1]) - 60
    cv2.imwrite(f'{OUT}/img/capfit_{R}_{i}.png', cv2.resize(im[y0:y0 + 120, x0:x0 + 120], None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST))
json.dump({k: np.mean(v, 0).tolist() for k, v in res.items()}, open(f'{OUT}/capfixed_{R}.json', 'w'))
