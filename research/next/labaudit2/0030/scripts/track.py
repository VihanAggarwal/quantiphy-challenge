"""Round-2 tracker for family 0030: red ball centre per video frame, read straight from the mp4s.
Estimators: (1) centroid of the red mask, (2) extent-box centre, (3) min-enclosing / fitted circle of the outer contour.
Prints per-step pixel displacements to locate the double-length (dropped capture frame) step."""
import cv2, numpy as np, json, sys
V = '/home/user/quantiphy-challenge/data/QuantiPhy/captured_0030%s.mp4'
OUT = '/home/user/quantiphy-challenge/research/next/labaudit2/0030/track.json'


def frames(r):
    c = cv2.VideoCapture(V % r)
    out = []
    while True:
        ok, im = c.read()
        if not ok:
            break
        out.append(im)
    return out


def mask(im, loose=False):
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    h, s, v = [hsv[..., k].astype(int) for k in range(3)]
    b, g, r = [im[..., k].astype(int) for k in range(3)]
    if loose:
        m = (((h <= 14) | (h >= 168)) & (s > 120) & (v > 90) & (r - g > 60))
    else:
        m = (((h <= 11) | (h >= 172)) & (s > 185) & (v > 100) & (r - g > 90))
    m = m.astype(np.uint8)
    m[:360] = 0; m[600:] = 0
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return m


def track(r, loose=False):
    fr = frames(r)
    tr = []; prev = None
    for i, im in enumerate(fr):
        m = mask(im, loose)
        n, lab, st, cen = cv2.connectedComponentsWithStats(m)
        cands = [k for k in range(1, n) if st[k, 4] > 60]
        if not cands:
            tr.append(None); continue
        if prev is None:
            k = max(cands, key=lambda k: st[k, 4])
        else:
            k = min(cands, key=lambda k: np.hypot(*(cen[k] - prev)) - 0.03 * st[k, 4])
        x, y, w, hh, a = st[k]
        comp = (lab == k).astype(np.uint8)
        # merge nearby components (reflection excluded by the row limit below the ball's bottom is not trivial; keep main)
        cnts, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cnt = max(cnts, key=cv2.contourArea)
        (ex, ey), er = cv2.minEnclosingCircle(cnt)
        tr.append(dict(cx=float(cen[k][0]), cy=float(cen[k][1]), bx=x + (w - 1) / 2, by=y + (hh - 1) / 2,
                       w=int(w), h=int(hh), a=int(a), ex=float(ex), ey=float(ey), er=float(er), top=int(y), bot=int(y + hh - 1)))
        prev = cen[k]
    return tr


if __name__ == '__main__':
    res = {}
    for r, key in [('s', 's'), ('', 'o'), ('x', 'x')]:
        res[key] = track(r, loose=(key == 'x'))
    json.dump(res, open(OUT, 'w'), indent=0)
    for i in range(49):
        row = [f'{i:2d}']
        for key in 'sox':
            t = res[key][i]
            if t is None:
                row.append('None'); continue
            p = res[key][i - 1] if i else None
            st = f"{np.hypot(t['cx']-p['cx'], t['cy']-p['cy']):5.1f}" if p else '  -  '
            row.append(f"{t['cx']:6.1f},{t['cy']:5.1f} bb{t['bx']:6.1f},{t['by']:5.1f} {t['w']:2d}x{t['h']:2d} a{t['a']:4d} step{st}")
        print(' | '.join(row))
