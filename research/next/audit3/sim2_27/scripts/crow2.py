# Route 2: per-frame subpixel tip-to-tail extent from a column-wise darkness profile
# (max darkness over body rows), half-contrast crossings; scale from beak-tip (leading edge) track.
import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0091.mp4')
fr = []
while True:
    ok, im = c.read()
    if not ok: break
    fr.append(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32))
bg = np.median(np.stack(fr[12:]), axis=0)
def extent(i, x0, x1, y0, y1):
    d = bg[y0:y1, x0:x1] - fr[i][y0:y1, x0:x1]   # bird darker than sky
    prof = d.max(axis=0)                         # column-wise max darkness
    pk = np.percentile(prof, 99)
    out = {}
    for frac in (0.25, 0.5):
        th = frac * pk
        idx = np.nonzero(prof > th)[0]
        l, r = idx[0], idx[-1]
        # subpixel interpolate crossings
        lf = l - 1 + (th - prof[l-1]) / (prof[l] - prof[l-1])
        rf = r + (prof[r] - th) / (prof[r] - prof[r+1])
        out[frac] = (x0 + lf, x0 + rf)
    return out
crow_boxes = {0: (1080, 1240), 1: (1080, 1240), 8: (1630, 1780), 9: (1700, 1860), 10: (1790, 1919)}
tips = {}
for i, (a, b) in crow_boxes.items():
    e = extent(i, a, b, 520, 630)
    tips[i] = e
    print('crow f%d' % i, {k: ('%.1f-%.1f len %.1f' % (v[0], v[1], v[1]-v[0])) for k, v in e.items()})
# beak tip (right edge, crow flies right) speed f1 -> f10 (half contrast)
for frac in (0.25, 0.5):
    v = (tips[10][frac][1] - tips[1][frac][1]) / 9
    vt = (tips[10][frac][0] - tips[1][frac][0]) / 9
    s = 11.0 / 24.0 / v
    L = np.mean([tips[k][frac][1]-tips[k][frac][0] for k in (0, 8, 9, 10)])
    print('frac', frac, 'beak px/frame %.2f tail px/frame %.2f scale %.6f m/px; mean len %.1f px -> %.3f m' % (v, vt, s, L, L*s))
for i, (a, b) in {0: (640, 840), 1: (640, 840)}.items():
    e = extent(i, a, b, 430, 610)
    print('eagle f%d' % i, {k: ('%.1f-%.1f len %.1f' % (v[0], v[1], v[1]-v[0])) for k, v in e.items()})
