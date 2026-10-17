"""Track the white ball per video frame in o / s / x renders.
Mask = |frame - background| where background = median of frames 44-48 (ball gone).  Sub-pixel extents:
left/right from the column profile of the mask in the upper half of the ball (lower half touches its shadow),
top from the row profile; circle fit (algebraic) to the upper-half contour points."""
import cv2, numpy as np, json, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0039/scripts')
from frames import load
OUT = '/home/user/quantiphy-challenge/research/next/labaudit2/0039'
def circfit(x, y):
    A = np.c_[2 * x, 2 * y, np.ones_like(x)]; b = x ** 2 + y ** 2
    c, *_ = np.linalg.lstsq(A, b, rcond=None); r = np.sqrt(c[2] + c[0] ** 2 + c[1] ** 2)
    return c[0], c[1], r
res = {}
for r in ['0039', '0039s', '0039x']:
    fr = load(r).astype(np.int16)
    bg = np.median(fr[44:49], axis=0)
    out = {}
    for i in range(10, 44):
        d = np.abs(fr[i] - bg).sum(-1)
        m = (d > 60).astype(np.uint8)
        m[:420] = 0; m[560:] = 0; m[:, 640:] = 0; m[:, :400] = 0
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(m)
        if n < 2: continue
        k = 1 + np.argmax(st[1:, 4])
        if st[k, 4] < 150: continue
        blob = (lab == k).astype(np.uint8)
        x0, y0, w, h = st[k, :4]
        ys, xs = np.nonzero(blob)
        top = ys.min()
        # upper half rows: top .. top + w/2
        cnts, _ = cv2.findContours(blob, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        c = max(cnts, key=cv2.contourArea)[:, 0, :].astype(float)
        up = c[c[:, 1] <= top + 0.55 * w]
        cx, cy, rad = circfit(up[:, 0], up[:, 1])
        # left/right extents in the upper half rows
        sub = blob[top:top + int(0.6 * w)]
        cols = np.nonzero(sub.any(0))[0]
        l, rr = cols.min(), cols.max()
        out[i] = dict(l=int(l), rr=int(rr), top=int(top), bot=int(ys.max()), w=int(rr - l + 1), area=int(st[k, 4]),
                      cfit=[float(cx), float(cy), float(rad)], cen=[float(cen[k][0]), float(cen[k][1])],
                      px=[(l + rr) / 2.0, top + (rr - l + 1) / 2.0])
    res[r] = out
    for i in sorted(out):
        o = out[i]
        print(r, i, 'px %.1f %.1f' % tuple(o['px']), 'cfit %.1f %.1f r%.1f' % tuple(o['cfit']), 'w', o['w'], 'h', o['bot'] - o['top'] + 1, 'area', o['area'])
json.dump(res, open(f'{OUT}/track.json', 'w'), indent=1)
