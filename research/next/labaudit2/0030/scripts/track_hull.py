"""Ball segmentation that keeps the specular highlights: a looser red mask seeded by the strict-core component,
closed, hole-filled, then the convex hull. Per frame: hull centroid, extent box (top/bot/left/right), fitted ellipse.
Writes track_hull.json and a crop sheet with the hull drawn."""
import cv2, numpy as np, json, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0030/scripts')
from track import frames, mask
D = '/home/user/quantiphy-challenge/research/next/labaudit2/0030/'
T = json.load(open(D + 'track.json'))


def loose(im):
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    h, s, v = [hsv[..., k].astype(int) for k in range(3)]
    b, g, r = [im[..., k].astype(int) for k in range(3)]
    m = (((h <= 12) | (h >= 170)) & (s > 110) & (v > 110) & (r - g > 55) & (r - b > 55))
    return m.astype(np.uint8)


def hull_track(r, key, rows_cut=None):
    fr = frames(r)
    out = []
    for k, im in enumerate(fr):
        t = T['s'][k] if T['s'][k] else T['o'][k]
        if t is None:
            out.append(None); continue
        cx, cy = t['cx'], t['cy']
        core = mask(im)
        m = loose(im)
        # highlights: bright low-saturation pixels inside the ball are added via hole filling of the closed mask
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
        n, lab, st, cen = cv2.connectedComponentsWithStats(m)
        # component that contains the strict-core centroid (or the nearest)
        lk = lab[int(round(cy)), int(round(cx))]
        if lk == 0:
            ks = [kk for kk in range(1, n) if st[kk, 4] > 50]
            lk = min(ks, key=lambda kk: np.hypot(*(cen[kk] - (cx, cy))))
        comp = (lab == lk).astype(np.uint8)
        cnts, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cnt = max(cnts, key=cv2.contourArea)
        hull = cv2.convexHull(cnt)
        hm = np.zeros_like(comp); cv2.fillPoly(hm, [hull], 1)
        ys, xs = np.nonzero(hm)
        M = cv2.moments(hull)
        hx, hy = M['m10'] / M['m00'], M['m01'] / M['m00']
        el = cv2.fitEllipse(cnt) if len(cnt) >= 5 else None
        out.append(dict(hx=hx, hy=hy, top=int(ys.min()), bot=int(ys.max()), left=int(xs.min()), right=int(xs.max()),
                        area=int(hm.sum()), el=el, hull=hull[:, 0, :].tolist()))
    return out, fr


if __name__ == '__main__':
    res = {}; frs = {}
    for r, key in [('s', 's'), ('', 'o')]:
        res[key], frs[key] = hull_track(r, key)
    json.dump({k: [dict((a, b) for a, b in d.items() if a != 'hull') if d else None for d in v] for k, v in res.items()},
              open(D + 'track_hull.json', 'w'), indent=0)
    for k in range(49):
        row = [f'v{k:2d}']
        for key in 'so':
            d = res[key][k]
            if d is None:
                row.append('None'); continue
            row.append(f"hull c({d['hx']:6.1f},{d['hy']:5.1f}) box c({(d['left']+d['right'])/2:6.1f},{(d['top']+d['bot'])/2:5.1f}) "
                       f"w{d['right']-d['left']+1:3d} h{d['bot']-d['top']+1:3d} top{d['top']} bot{d['bot']}")
        print(' | '.join(row))
    # crop sheet
    key = sys.argv[1] if len(sys.argv) > 1 else 's'
    ks = [int(x) for x in (sys.argv[2] if len(sys.argv) > 2 else '0,3,5,6,9,10,11,12,14,15,19,20').split(',')]
    tiles = []
    for k in ks:
        d = res[key][k]; im = frs[key][k].copy()
        cv2.polylines(im, [np.array(d['hull'], np.int32)], True, (0, 255, 0), 1)
        cx, cy = int(d['hx']), int(d['hy']); h = 45
        cr = im[cy - h:cy + h, cx - h:cx + h]
        cr = cv2.resize(cr, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
        cv2.drawMarker(cr, (int((d['hx'] - cx + h) * 3), int((d['hy'] - cy + h) * 3)), (255, 0, 0), cv2.MARKER_CROSS, 18, 1)
        cv2.putText(cr, f'v{k}', (5, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        tiles.append(cr)
    rows = [np.hstack(tiles[i:i + 4]) for i in range(0, len(tiles), 4)]
    cv2.imwrite(D + f'img/hull_{key}.png', np.vstack(rows))
