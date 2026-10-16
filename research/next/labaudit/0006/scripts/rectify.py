"""Rectify table top (frame 0) for several f; report aspect ratio and scale for W=76 or W=60.3."""
import numpy as np
D = '/home/user/quantiphy-challenge/research/next/labaudit/0006/'
C = np.load(D + 'scripts/corners.npy')  # BL BR FR FL
cx, cy = 640.0, 360.0
def plane(f, C=C):
    r = np.c_[C[:, 0] - cx, C[:, 1] - cy, np.full(4, f)]
    # VPs
    def line(p, q): return np.cross(np.r_[p, 1], np.r_[q, 1])
    v1 = np.cross(line(C[3], C[0]), line(C[2], C[1]))  # depth dir (left/right edges)
    v2 = np.cross(line(C[0], C[1]), line(C[3], C[2]))  # width dir
    d1 = np.array([v1[0] - cx * v1[2], v1[1] - cy * v1[2], f * v1[2]]); d1 /= np.linalg.norm(d1)
    d2 = np.array([v2[0] - cx * v2[2], v2[1] - cy * v2[2], f * v2[2]]); d2 /= np.linalg.norm(d2)
    n = np.cross(d1, d2); n /= np.linalg.norm(n)
    if n[1] > 0: n = -n  # normal pointing up (toward -y)
    t = 1.0 / (r @ n)  # n.X = 1 (plane at distance 1 along n) -> scale later
    X = r * t[:, None]
    return X, n, d1, d2
for f in [600, 650, 700, 711, 750, 800]:
    X, n, d1, d2 = plane(f)
    w_back = np.linalg.norm(X[1] - X[0]); w_front = np.linalg.norm(X[2] - X[3])
    dl = np.linalg.norm(X[3] - X[0]); dr = np.linalg.norm(X[2] - X[1])
    W = (w_back + w_front) / 2; Dp = (dl + dr) / 2
    s = 0.76 / W
    print('f=%d  W/D=%.3f  (wb %.3f wf %.3f dl %.3f dr %.3f)  angle d1.d2=%.2f deg  if W=76: h=%.3f m, D=%.1f cm, Zfront=%.3f Zback=%.3f, cam height %.3f'
          % (f, W / Dp, w_back / W, w_front / W, dl / Dp, dr / Dp, np.degrees(np.arccos(abs(d1 @ d2))), s, Dp * s * 100, X[3, 2] * s, X[0, 2] * s, s))
