import cv2, numpy as np, json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from frames import load
OUT = os.path.join(os.path.dirname(__file__), '..', 'track.json')
ROI = (480, 330, 900, 500)  # x0,y0,x1,y1
def teal(im):
    x0, y0, x1, y1 = ROI
    sub = im[y0:y1, x0:x1]
    b, g, r = [sub[..., i].astype(int) for i in range(3)]
    m = ((b - r > 12) & (g - r > 8) & (g > 100) & (np.abs(b - g) < 22)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n < 2: return None
    k = 1 + np.argmax(st[1:, 4])
    st = st[k].copy(); st[0] += x0; st[1] += y0
    return (lab == k), st, cen[k] + [x0, y0]
if __name__ == '__main__':
    res = {}
    for tag in ['', 's', 'x']:
        fr = load(tag); rows = []
        for i, im in enumerate(fr):
            t = teal(im)
            if t is None: rows.append(None); continue
            m, st, c = t
            x, y, w, h, a = [int(v) for v in st]
            rows.append(dict(k=i, cx=float(c[0]), cy=float(c[1]), bx=x + w / 2, by=y + h / 2, x0=x, y0=y, x1=x + w, y1=y + h, area=a))
        res[tag or 'o'] = rows
    json.dump(res, open(OUT, 'w'), indent=0)
    for i in range(16, 40):
        s = '%2d' % i
        for tag in res:
            r = res[tag][i]; p = res[tag][i - 1]
            s += ' | %s c(%6.1f,%6.1f) bb(%6.1f,%6.1f) a%5d dc %5.1f' % (tag, r['cx'], r['cy'], r['bx'], r['by'], r['area'], np.hypot(r['cx'] - p['cx'], r['cy'] - p['cy']))
        print(s)
