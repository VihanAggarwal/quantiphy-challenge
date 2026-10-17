"""Sub-pixel half-level chord measurement of both balls (o and x renders).
For every row through the ball: left/right crossings of the half level between ball and surroundings.
Diameter from (a) circle chord fit (w^2 + 4y^2 = a + 8 yc y), using rows of the upper ~75% of the ball
(bottom has the contact shadow), (b) max of a free quadratic fit of w(y) near the widest rows.
Output ../chords_<render>.json
"""
import cv2, numpy as np, json, sys

R = sys.argv[1] if len(sys.argv) > 1 else 'o'
vid = {'o': 'captured_0031', 's': 'captured_0031s', 'x': 'captured_0031x'}[R]
cap = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    frames.append(f)
tr = json.load(open(f'/home/user/quantiphy-challenge/research/next/labaudit2/0031/track_x.json'))


def crossings(row, x0, thr):
    """from x0 (inside) go left and right until row < thr; sub-pixel interpolation"""
    n = len(row)
    xl = xr = None
    for x in range(int(x0), 0, -1):
        if row[x] < thr:
            xl = x + (thr - row[x]) / (row[x + 1] - row[x] + 1e-9); break
    for x in range(int(x0), n - 1):
        if row[x] < thr:
            xr = x - (thr - row[x]) / (row[x - 1] - row[x] + 1e-9); break
    return xl, xr


def measure(ch, cx, cy, r0):
    ch = cv2.GaussianBlur(ch, (0, 0), 0.7)
    y0, y1 = int(cy - r0 * 1.3), int(cy + r0 * 1.3)
    inner = np.median(ch[int(cy - r0 * 0.4):int(cy + r0 * 0.4), int(cx - r0 * 0.4):int(cx + r0 * 0.4)])
    rows = []
    for y in range(y0, y1 + 1):
        row = ch[y]
        if row[int(cx)] < 0.75 * inner: continue
        # local outside level: median of pixels 1.6 r0 .. 2.0 r0 left and right
        oL = np.median(row[max(0, int(cx - 2.0 * r0)):int(cx - 1.5 * r0)])
        oR = np.median(row[int(cx + 1.5 * r0):int(cx + 2.0 * r0)])
        out = 0.5 * (oL + oR)
        thr = 0.5 * (inner + out)
        xl, xr = crossings(row, cx, thr)
        if xl is None or xr is None: continue
        rows.append((y, xl, xr))
    rows = np.array(rows)
    if len(rows) < 6: return None
    y, xl, xr = rows.T
    w = xr - xl
    top, bot = y.min(), y.max()
    H = bot - top
    # (a) circle chord fit on upper 75%
    sel = (y <= top + 0.75 * H) & (w > 0.3 * w.max())
    A = np.c_[np.ones(sel.sum()), 8 * y[sel]]
    a, ycf = np.linalg.lstsq(A, w[sel] ** 2 + 4 * y[sel] ** 2, rcond=None)[0]
    dcf = np.sqrt(max(a + 4 * ycf ** 2, 0))
    # (b) free quadratic around the widest rows
    k = np.argmax(w)
    selb = np.abs(y - y[k]) <= max(3, 0.25 * H)
    if selb.sum() >= 4:
        p = np.polyfit(y[selb], w[selb], 2)
        if p[0] < 0:
            yb = -p[1] / (2 * p[0]); dq = np.polyval(p, yb)
        else:
            yb = y[k]; dq = w[k]
    else:
        yb = y[k]; dq = w[k]
    xc = np.mean(0.5 * (xl + xr)[sel])
    return dict(xc=float(xc), yc_fit=float(ycf), d_circ=float(dcf), d_quad=float(dq), y_quad=float(yb),
                top=float(top), bot=float(bot), wmax=float(w.max()), ymid=float(0.5 * (top + bot)))


out = []
for i, f in enumerate(frames):
    f = f.astype(np.float32)
    B, G, Rr = f[..., 0], f[..., 1], f[..., 2]
    yel = np.minimum(Rr, G) - B
    wht = f.min(2)
    rec = {'i': i}
    t = tr[i].get('T'); w = tr[i].get('W')
    if t and i <= 42:
        r0 = max(t['bw'], t['bh']) / 2
        m = measure(yel, t['bcx'], t['bcy'], r0)
        if m: rec['T'] = m
    if w:
        r0 = max(w['bw'], w['bh']) / 2
        m = measure(wht, w['bcx'], w['bcy'], r0)
        if m: rec['W'] = m
    out.append(rec)
    s = '%2d' % i
    for k in ('T', 'W'):
        if k in rec:
            m = rec[k]
            s += ' | %s x=%.1f yc=%.1f top=%.1f bot=%.1f dcirc=%.2f dquad=%.2f' % (k, m['xc'], m['yc_fit'], m['top'], m['bot'], m['d_circ'], m['d_quad'])
    print(s)
json.dump(out, open(f'/home/user/quantiphy-challenge/research/next/labaudit2/0031/chords_{R}.json', 'w'))
