"""Background-difference toy silhouette (includes the grey face patch) for the fall, v19-v33, o and s renders.
bg = median of video frames 38-47 (toy low-left on/below the table, arm still)."""
import cv2, numpy as np, json, sys
from common import *
out = {}
for tag in ('o', 's'):
    fr = load(tag)
    bg = np.median(np.stack([fr[i] for i in range(38, 48)]).astype(np.float32), axis=0)
    out[tag] = {}
    for i in range(19, 34):
        d = np.abs(fr[i].astype(np.float32) - bg).max(axis=2)
        roi = np.zeros(d.shape, bool); roi[90:500, 480:680] = True
        for thr in (25, 40):
            m = ((d > thr) & roi).astype(np.uint8)
            m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
            m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
            n, lab, st, cen = cv2.connectedComponentsWithStats(m)
            if n <= 1: continue
            k = 1 + np.argmax(st[1:, 4]); x, y, w, h, a = st[k]
            mk = (lab == k).astype(np.uint8)
            cnts, _ = cv2.findContours(mk, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            hull = cv2.convexHull(max(cnts, key=cv2.contourArea)); hm = np.zeros_like(mk); cv2.fillPoly(hm, [hull], 1)
            ys, xs = np.nonzero(hm)
            r = dict(c=[float(cen[k][0]), float(cen[k][1])], bc=[x + w / 2., y + h / 2.], hc=[float(xs.mean()), float(ys.mean())], box=[int(x), int(y), int(w), int(h)], area=int(a))
            out[tag]['%d_%d' % (i, thr)] = r
            print(tag, i, thr, 'c(%.1f,%.1f) bc(%.1f,%.1f) hc(%.1f,%.1f) box%s a%d' % (*r['c'], *r['bc'], *r['hc'], r['box'], a))
        if tag == 'o' and i in (24, 27, 29, 30, 31):
            vis = fr[i].copy(); vis[(d > 25)] = (vis[(d > 25)] * 0.5 + np.array([255, 0, 255]) * 0.5).astype(np.uint8)
            cv2.imwrite(D + 'img/bgdiff_v%d.png' % i, cv2.resize(vis[100:470, 480:680], (400, 740), interpolation=cv2.INTER_NEAREST))
json.dump(out, open(D + 'bgtrack.json', 'w'), indent=1)
