"""Toy track on the o render: yellow mask, component nearest previous position; centroid, bbox centre, hole-filled hull centroid."""
import cv2, numpy as np, json, sys
from common import *
tag = sys.argv[1] if len(sys.argv) > 1 else 'o'
smin = int(sys.argv[2]) if len(sys.argv) > 2 else 90
fr = load(tag)
out = {}; prev = np.array([611., 225.])
for i in range(0, 48):
    hsv = cv2.cvtColor(fr[i], cv2.COLOR_BGR2HSV)
    m = cv2.inRange(hsv, (15, smin, 90), (40, 255, 255))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    best = None
    for k in range(1, n):
        if st[k][4] < 150: continue
        d = np.linalg.norm(cen[k] - prev)
        sc = d - 0.02 * st[k][4]
        if d < 200 and (best is None or sc < best[0]): best = (sc, k)
    if best is None: print(i, None); continue
    k = best[1]
    mk = (lab == k).astype(np.uint8)
    cnts, _ = cv2.findContours(mk, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    hull = cv2.convexHull(max(cnts, key=cv2.contourArea))
    hm = np.zeros_like(mk); cv2.fillPoly(hm, [hull], 1)
    ys, xs = np.nonzero(hm)
    x, y, w, h = st[k][:4]
    r = dict(c=[float(cen[k][0]), float(cen[k][1])], bc=[x + w / 2, y + h / 2], hc=[float(xs.mean()), float(ys.mean())],
             box=[int(x), int(y), int(w), int(h)], area=int(st[k][4]), harea=int(hm.sum()))
    out[i] = r; prev = cen[k]
    print(i, 'c(%.1f,%.1f) bc(%.1f,%.1f) hc(%.1f,%.1f) box%s area%d hull%d' % (*r['c'], *r['bc'], *r['hc'], r['box'], r['area'], r['harea']))
json.dump(out, open(D + 'track_%s_s%d.json' % (tag, smin), 'w'), indent=1)
