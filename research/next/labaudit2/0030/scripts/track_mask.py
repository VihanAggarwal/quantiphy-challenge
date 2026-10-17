"""Ball silhouette from the x render: in x the ball's SAM mask region is drawn as a dull brown fill while the table is
identical to the s render and the background is black. Mask = |s - x| large and x not black. Gives the full silhouette
(highlights and blurred rim included, table reflection excluded). Per frame: mask centroid, extent box, area, equivalent
diameter, vertical extent, and an ellipse fit. Falls back to None where x shows no fill (fast front frames)."""
import cv2, numpy as np, json, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0030/scripts')
from track import frames
D = '/home/user/quantiphy-challenge/research/next/labaudit2/0030/'
H = json.load(open(D + 'track_hull.json'))['s']


def ball_mask(s, x, cx, cy, win=70):
    y0, x0 = max(int(cy) - win, 0), max(int(cx) - win, 0)
    ss = s[y0:int(cy) + win, x0:int(cx) + win].astype(int)
    xx = x[y0:int(cy) + win, x0:int(cx) + win].astype(int)
    d = np.abs(ss - xx).sum(2)
    xs = xx.sum(2)
    m = ((d > 60) & (xs > 60)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n < 2:
        return None
    lc = (int(cx) - x0, int(cy) - y0)
    k = lab[lc[1], lc[0]]
    if k == 0:
        ks = [kk for kk in range(1, n) if st[kk, 4] > 50]
        if not ks:
            return None
        k = min(ks, key=lambda kk: np.hypot(*(cen[kk] - lc)))
    comp = (lab == k).astype(np.uint8)
    # fill holes
    cnts, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnt = max(cnts, key=cv2.contourArea)
    filled = np.zeros_like(comp); cv2.drawContours(filled, [cnt], -1, 1, -1)
    return filled, x0, y0, cnt


def run():
    S = frames('s'); X = frames('x')
    out = []
    for k in range(49):
        h = H[k]
        if h is None:
            out.append(None); continue
        r = ball_mask(S[k], X[k], h['hx'], h['hy'])
        if r is None:
            out.append(None); continue
        m, x0, y0, cnt = r
        ys, xs = np.nonzero(m)
        a = len(xs)
        el = cv2.fitEllipse(cnt + np.array([x0, y0])) if len(cnt) >= 5 else None
        # circle fit to the upper half of the contour (least blurred against the background)
        c = cnt[:, 0, :].astype(float) + (x0, y0)
        out.append(dict(mx=float(xs.mean() + x0), my=float(ys.mean() + y0), top=int(ys.min() + y0), bot=int(ys.max() + y0),
                        left=int(xs.min() + x0), right=int(xs.max() + x0), area=int(a), deq=float(np.sqrt(4 * a / np.pi)),
                        el=el))
    return out, S, X


if __name__ == '__main__':
    out, S, X = run()
    json.dump(out, open(D + 'track_mask.json', 'w'), indent=0)
    def cap(k): return k + (k >= 12) + (k >= 36)
    prev = None
    for k, d in enumerate(out):
        if d is None:
            print(f'v{k:2d} n{cap(k):2d} None'); prev = None; continue
        st = f"{np.hypot(d['mx']-prev['mx'], d['my']-prev['my']):5.1f}" if prev else '  -  '
        print(f"v{k:2d} n{cap(k):2d} c({d['mx']:6.1f},{d['my']:5.1f}) box({(d['left']+d['right'])/2:6.1f},{(d['top']+d['bot'])/2:5.1f}) "
              f"w{d['right']-d['left']+1:3d} h{d['bot']-d['top']+1:3d} deq{d['deq']:5.1f} el({d['el'][1][0]:.1f},{d['el'][1][1]:.1f},{d['el'][2]:.0f}) step{st}")
        prev = d
    ks = [int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else '4,5,6,7,9,10,11,12,14,15,19,20').split(',')]
    tiles = []
    for k in ks:
        d = out[k]
        if d is None:
            continue
        im = S[k].copy()
        r = ball_mask(S[k], X[k], H[k]['hx'], H[k]['hy'])
        cnt = r[3] + np.array([r[1], r[2]])
        cv2.drawContours(im, [cnt], -1, (0, 255, 0), 1)
        cx, cy = int(d['mx']), int(d['my']); hh = 45
        cr = im[cy - hh:cy + hh, cx - hh:cx + hh]
        cr = cv2.resize(cr, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
        cv2.drawMarker(cr, (int((d['mx'] - cx + hh) * 3), int((d['my'] - cy + hh) * 3)), (255, 0, 0), cv2.MARKER_CROSS, 18, 1)
        cv2.putText(cr, f'v{k}', (5, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        tiles.append(cr)
    while len(tiles) % 4:
        tiles.append(np.zeros_like(tiles[0]))
    rows = [np.hstack(tiles[i:i + 4]) for i in range(0, len(tiles), 4)]
    cv2.imwrite(D + 'img/mask_s.png', np.vstack(rows))
