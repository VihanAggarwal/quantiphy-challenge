"""Ball centre per video frame on the o/s/x renders (frames held in memory only).
Centre = centroid of the white blob (min channel above a threshold, inside a window around the previous position);
also the bounding extents (half-max) for size. Output: track.json {render: [[u, v, w, h, area], ...]}."""
import sys, json, cv2, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0022/scripts')
from common import *
out = {}
for tag in ['x', 'o', 's']:
    fr = frames(tag).astype(np.float32)
    med = np.median(fr, axis=0)
    prev = np.array([437.6, 380.0]); res = []
    for k, im in enumerate(fr):
        u0, v0 = int(prev[0]), int(prev[1])
        y0, x0 = max(0, v0 - 30), max(0, u0 - 30)
        win = im[y0:v0 + 40, x0:u0 + 30]
        mn = win.min(2)                      # white ball: high min channel; wood is low in blue
        bg = med[y0:v0 + 40, x0:u0 + 30].min(2)
        sc = mn - np.minimum(bg, 120)        # brightness above wood
        thr = 0.5 * (np.percentile(mn, 99.8) + np.median(mn))
        m = (mn > thr).astype(np.uint8)
        n, lab, st, cen = cv2.connectedComponentsWithStats(m)
        if n < 2:
            res.append(None); print(tag, k, None); continue
        j = 1 + int(np.argmax(st[1:, 4]))
        msk = lab == j
        wts = (mn - np.median(mn)) * msk
        ys, xs = np.mgrid[0:mn.shape[0], 0:mn.shape[1]]
        cu = (wts * xs).sum() / wts.sum() + x0; cv = (wts * ys).sum() / wts.sum() + y0
        x, y, w, h, a = st[j]
        res.append([float(cu), float(cv), int(w), int(h), int(a), float(thr)])
        prev = np.array([cu, cv])
    out[tag] = res
    print(tag, [None if r is None else (round(r[0], 1), round(r[1], 1), r[2], r[3]) for r in res])
json.dump(out, open(f'{B}/track.json', 'w'))
