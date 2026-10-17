"""Connected components of the x-render matte (non-white) per frame, excluding the two persons."""
import sys, json
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0018/scripts')
from common import *
fr = frames('x')
res = {}
for k in range(len(fr)):
    im = fr[k].astype(int)
    m = (np.abs(im - 255).max(2) > 30).astype(np.uint8)
    m[690:, 1000:] = 0  # watermark
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    comps = []
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if a < 40 or a > 20000: continue
        pix = fr[k][lab == i].mean(0)
        comps.append(dict(x=int(x), y=int(y), w=int(w), h=int(h), a=int(a), cx=round(float(cen[i][0]), 2), cy=round(float(cen[i][1]), 2), bgr=[int(c) for c in pix]))
    res[k] = comps
    print(k, [(c['cx'], c['cy'], c['w'], c['h'], c['a'], c['bgr']) for c in sorted(comps, key=lambda c: c['cx'])])
json.dump(res, open(OUT + 'track_x_raw.json', 'w'))
