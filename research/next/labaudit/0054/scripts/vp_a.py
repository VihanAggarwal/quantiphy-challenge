"""Vertical vanishing point in camera a (0054a frame 0) from near-vertical line segments -> gravity direction."""
import cv2, numpy as np
F, CX, CY = 711.0, 640.0, 360.0
im = cv2.imread('/home/user/quantiphy-challenge/research/next/labaudit/0054/frames/a_00.png')
g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
lsd = cv2.createLineSegmentDetector(0)
lines = np.asarray(lsd.detect(g)[0]).reshape(-1, 4)
L = []
for x1, y1, x2, y2 in lines:
    dx, dy = x2 - x1, y2 - y1
    ln = np.hypot(dx, dy)
    if ln < 80: continue
    ang = np.degrees(np.arctan2(abs(dx), abs(dy)))
    if ang > 8: continue
    L.append((x1, y1, x2, y2, ln))
L = np.array(L)
print(len(L), 'segments')
# homogeneous lines in normalized camera coords
def hl(x1, y1, x2, y2):
    p = np.array([(x1 - CX) / F, (y1 - CY) / F, 1.0]); q = np.array([(x2 - CX) / F, (y2 - CY) / F, 1.0])
    l = np.cross(p, q); return l / np.linalg.norm(l)
H = np.array([hl(*s[:4]) for s in L])
W = L[:, 4]
# VP direction v minimises sum w (l.v)^2 -> smallest eigenvector
for it in range(3):
    M = (H * W[:, None]).T @ H
    ev, evec = np.linalg.eigh(M)
    v = evec[:, 0]
    if v[1] < 0: v = -v
    res = np.abs(H @ v)
    keep = res < np.percentile(res, 80)
    H, W, L = H[keep], W[keep], L[keep]
print('gravity dir in cam coords', v, 'pitch(deg, + = looking down)', np.degrees(np.arcsin(v[2])), 'roll', np.degrees(np.arctan2(v[0], v[1])))
for s in L[:40]:
    print('%.0f,%.0f -> %.0f,%.0f len %.0f' % tuple(s))
