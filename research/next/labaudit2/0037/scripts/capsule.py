"""Capsule (motion-blurred disc) fit to the ball mask on the x render (black background) and the s render.
Mask = background-difference blob from track.py (ball pixels only; frames where an object is drawn over the ball
are flagged). Model: set of points within distance r of a segment (centre c, half-length a, angle th).
Fit by maximising IoU with a 4x supersampled rendering (Nelder-Mead). Outputs capsule centre and diameter 2r.
Writes capsule.json {render: {frame: {cu, cv, r2, a, th, iou}}}."""
import sys, json, cv2, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0037/scripts')
from common import frames, OUT
from nm import nelder_mead

TR = json.load(open(OUT + '/track.json'))
SS = 4


def capsule_mask(shape, x0, y0, cu, cv_, a, r, th):
    H, W = shape
    ys, xs = np.mgrid[0:H * SS, 0:W * SS]
    X = x0 + (xs + 0.5) / SS - 0.5; Y = y0 + (ys + 0.5) / SS - 0.5
    dx, dy = np.cos(th), np.sin(th)
    px, py = X - cu, Y - cv_
    s = np.clip(px * dx + py * dy, -a, a)
    d2 = (px - s * dx) ** 2 + (py - s * dy) ** 2
    m = (d2 <= r * r).astype(np.float32)
    return m.reshape(H, SS, W, SS).mean(axis=(1, 3))


def fit(mask, x0, y0, init):
    def cost(p):
        cu, cv_, a, r, th = p
        if r <= 3 or a < 0:
            return 2.0
        m = capsule_mask(mask.shape, x0, y0, cu, cv_, a, r, th)
        inter = np.minimum(m, mask).sum(); uni = np.maximum(m, mask).sum()
        return 1 - inter / uni
    best = None
    for th0 in (init[4], init[4] + 0.3, init[4] - 0.3):
        p0 = np.array([init[0], init[1], init[2], init[3], th0])
        x, fv = nelder_mead(cost, p0, step=[1.0, 1.0, 1.0, 1.0, 0.1], xatol=0.01, fatol=1e-6)
        if best is None or fv < best[1]:
            best = (x, fv)
    return best[0], 1 - best[1]


if __name__ == '__main__':
    out = {}
    for r in ('x', 's'):
        fr = frames(r)
        med = np.median(np.stack(fr).astype(np.float32), axis=0)
        tr = TR[r]
        res = {}
        for n in range(12, 49):
            e = tr.get(str(n))
            if e is None:
                continue
            x0, y0 = e['bx0'] - 6, e['by0'] - 6
            x1, y1 = e['bx1'] + 7, e['by1'] + 7
            f = fr[n][y0:y1, x0:x1].astype(np.float32)
            d = np.abs(f - med[y0:y1, x0:x1]).sum(2)
            hsv = cv2.cvtColor(fr[n][y0:y1, x0:x1], cv2.COLOR_BGR2HSV)
            m = ((d > 60) & (hsv[..., 2] > 130) & (hsv[..., 1] < 90)).astype(np.uint8)
            nlab, lab, sts, cen = cv2.connectedComponentsWithStats(m)
            if nlab < 2:
                continue
            k = 1 + np.argmax(sts[1:, 4])
            mask = (lab == k).astype(np.float32)
            L = e['emaj']; Dm = e['emin']
            th = np.radians(e['eang'] + 90)   # cv2 fitEllipse angle -> major axis direction
            init = [e['u'], e['v'], max((L - Dm) / 2, 0.5), Dm / 2, th]
            p, iou = fit(mask, x0, y0, init)
            res[n] = dict(cu=round(float(p[0]), 2), cv=round(float(p[1]), 2), a=round(float(abs(p[2])), 2),
                          r2=round(float(2 * p[3]), 2), th=round(float(np.degrees(p[4]) % 180), 1), iou=round(float(iou), 4))
            print(r, n, res[n], 'centroid', e['u'], e['v'], 'emin', e['emin'])
        out[r] = res
    json.dump(out, open(OUT + '/capsule.json', 'w'), indent=0)
