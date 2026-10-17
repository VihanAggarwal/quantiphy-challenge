"""Track both tennis balls in camera a (ax render, hue mask) -> per-frame centroid, bbox, vertical extent.
Ball identity by proximity; merged blob at the collision frame split at the midpoint."""
import cv2, numpy as np, sys, json
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0034/scripts')
from frames import read
O = '/home/user/quantiphy-challenge/research/next/labaudit2/0034/'

def mask(im):
    h = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    H, S, V = h[..., 0], h[..., 1], h[..., 2]
    m = ((S > 80) & (V > 60) & (H >= 25) & (H <= 42)).astype(np.uint8)
    return cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))

def stats(m):
    ys, xs = np.nonzero(m)
    if len(xs) == 0: return None
    cols = {}
    for x, y in zip(xs, ys):
        a = cols.setdefault(x, [y, y]); a[0] = min(a[0], y); a[1] = max(a[1], y)
    hts = np.array([b - a + 1 for a, b in cols.values()])
    return dict(cx=float(xs.mean()), cy=float(ys.mean()), x0=int(xs.min()), x1=int(xs.max()), y0=int(ys.min()), y1=int(ys.max()),
                area=int(len(xs)), hmax=float(np.percentile(hts, 95)), bbox_cx=(xs.min() + xs.max()) / 2, bbox_cy=(ys.min() + ys.max()) / 2)

def run(v, init):
    fr = read(v); prev = dict(init); out = {'L': [], 'R': []}
    for i, im in enumerate(fr):
        m = mask(im)
        n, lab, st, cen = cv2.connectedComponentsWithStats(m)
        comps = [k for k in range(1, n) if st[k][4] >= 150]
        assign = {}
        for b in ('L', 'R'):
            d = [(np.hypot(cen[k][0] - prev[b][0], cen[k][1] - prev[b][1]), k) for k in comps]
            d.sort(); assign[b] = d[0][1] if d else None
        res = {}
        if assign['L'] == assign['R'] and assign['L'] is not None:   # merged: split at midpoint of bbox
            k = assign['L']; mm = (lab == k)
            xs = np.nonzero(mm)[1]; xm = (xs.min() + xs.max()) / 2
            for b, sel in (('L', np.arange(m.shape[1]) < xm), ('R', np.arange(m.shape[1]) >= xm)):
                s = stats(mm & sel[None, :]); s['merged'] = True; res[b] = s
        else:
            for b in ('L', 'R'):
                k = assign[b]
                s = stats(lab == k); s['merged'] = False; res[b] = s
        for b in ('L', 'R'):
            res[b]['f'] = i; out[b].append(res[b]); prev[b] = (res[b]['cx'], res[b]['cy'])
    return out

if __name__ == '__main__':
    v = sys.argv[1]
    init = {'L': (264, 483), 'R': (1028, 487)} if v.startswith('a') else {'L': (468, 289), 'R': (818, 259)}
    out = run(v, init)
    json.dump(out, open(O + f'track_{v}.json', 'w'), indent=0, default=float)
    for i in range(len(out['L'])):
        l, r = out['L'][i], out['R'][i]
        print(i, 'L %.1f %.1f w%d h%d hm%.0f a%d' % (l['cx'], l['cy'], l['x1']-l['x0']+1, l['y1']-l['y0']+1, l['hmax'], l['area']),
              '| R %.1f %.1f w%d h%d hm%.0f a%d' % (r['cx'], r['cy'], r['x1']-r['x0']+1, r['y1']-r['y0']+1, r['hmax'], r['area']), 'M' if l['merged'] else '')
