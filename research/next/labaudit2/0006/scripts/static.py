"""Toy height/width at the stated range (t=1.0 s, v24, R=1.402): silhouette extents from the s render (uniform background)
and the o render yellow mask; extents back-projected at the stated range (label style: two clicks, same range)."""
import cv2, numpy as np
from common import *
fs = load('s'); fo = load('o')
def ext(m):
    ys, xs = np.nonzero(m)
    return xs.min(), xs.max(), ys.min(), ys.max()
for i in (23, 24, 25, 26):
    img = fs[i].astype(np.float32)
    bgc = np.median(img[60:100, 520:560].reshape(-1, 3), axis=0)
    d = np.abs(img - bgc).max(axis=2)
    roi = np.zeros(d.shape, bool); roi[95:200, 555:660] = True
    out = []
    for thr in (30, 50):
        m = ((d > thr) & roi).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(m)
        k = 1 + np.argmax(st[1:, 4]); x0, x1, y0, y1 = ext(lab == k)
        out.append((thr, x0, x1, y0, y1))
    hsv = cv2.cvtColor(fo[i], cv2.COLOR_BGR2HSV)
    my = cv2.inRange(hsv, (15, 90, 90), (40, 255, 255)) > 0
    my &= roi
    x0, x1, y0, y1 = ext(my)
    out.append(('o-yellow', x0, x1, y0, y1))
    for (thr, x0, x1, y0, y1) in out:
        w, h = x1 - x0 + 1, y1 - y0 + 1
        uc, vc = (x0 + x1) / 2, (y0 + y1) / 2
        R = 1.402 if i == 24 else None
        Rs = [1.402] if i == 24 else [1.402]
        Wc = 100 * np.linalg.norm(P(x0 - 0.5, vc, 1.402) - P(x1 + 0.5, vc, 1.402))
        Hc = 100 * np.linalg.norm(P(uc, y0 - 0.5, 1.402) - P(uc, y1 + 0.5, 1.402))
        print('v%d %-9s x %d-%d y %d-%d: w %d h %d px -> at R 1.402: W %.2f H %.2f cm' % (i, thr, x0, x1, y0, y1, w, h, Wc, Hc))
