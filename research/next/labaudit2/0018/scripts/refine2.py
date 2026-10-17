"""Weighted centroid of |frame - clean bg| inside the x-matte component window, v26..48, for each object."""
import sys, json
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0018/scripts')
from common import *
fo = frames('').astype(np.float32); fx = frames('x')
bg = np.load('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/bg0018.npy')
raw = json.load(open(OUT + 'track_x_raw.json'))
lanes = dict(box=(440, 515), soccer=(515, 580), tennis=(730, 780), pine=(825, 900))
res = {k: {} for k in lanes}
for v in range(28, 49):
    for name, (a, b) in lanes.items():
        cs = [c for c in raw[str(v)] if a <= c['cx'] < b]
        if name == 'box' and v >= 40: cs = [c for c in raw[str(v)] if 400 <= c['cx'] < 500]
        if not cs: continue
        c = max(cs, key=lambda c: c['a'])
        x0, y0, x1, y1 = c['x'] - 6, c['y'] - 6, c['x'] + c['w'] + 6, c['y'] + c['h'] + 6
        d = np.abs(fo[v, y0:y1, x0:x1] - bg[y0:y1, x0:x1]).sum(2)
        d = np.nan_to_num(d)
        w = np.clip(d - 30, 0, None)
        yy, xx = np.mgrid[y0:y1, x0:x1]
        if w.sum() == 0: continue
        cx = (w * xx).sum() / w.sum(); cy = (w * yy).sum() / w.sum()
        # matte centroid and horizontal width (median row width of matte)
        m = (np.abs(fx[v, y0:y1, x0:x1].astype(int) - 255).max(2) > 30)
        rw = m.sum(1); rw = rw[rw > 0]
        res[name][v] = dict(mx=c['cx'], my=c['cy'], ox=round(float(cx), 2), oy=round(float(cy), 2), mw=float(np.median(rw)), mwmax=int(rw.max()), mh=c['h'], top=c['y'], bot=c['y'] + c['h'] - 1)
json.dump(res, open(OUT + 'track_refined.json', 'w'), indent=0)
for name in lanes:
    print('==', name)
    for v, r in res[name].items():
        print(v, r)
