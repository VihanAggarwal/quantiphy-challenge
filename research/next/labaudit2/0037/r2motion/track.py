"""Independent ball tracker for captured_0037{,s,x}. Median-background differencing + white blob."""
import sys, json
import cv2, numpy as np

V = '/home/user/quantiphy-challenge/data/QuantiPhy/captured_0037%s.mp4'


def load(sfx):
    c = cv2.VideoCapture(V % sfx)
    fr = []
    while True:
        ok, f = c.read()
        if not ok:
            break
        fr.append(f)
    return fr


def track(sfx, dbg=False):
    fr = load(sfx)
    med = np.median(np.stack(fr[::2]), axis=0).astype(np.uint8)
    out = []
    prev = None
    for i, f in enumerate(fr):
        d = cv2.absdiff(f, med).max(axis=2)
        hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
        white = (hsv[..., 2] > 150) & (hsv[..., 1] < 70)
        m = ((d > 40) & white).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(m)
        best = None
        for k in range(1, n):
            a = st[k, 4]
            if a < 60:
                continue
            x, y, w, h = st[k, :4]
            if w > 120 or h > 120:
                continue
            fill = a / (w * h)
            score = a * fill
            if prev is not None:
                dist = np.hypot(cen[k][0] - prev[0], cen[k][1] - prev[1])
                if dist > 150:
                    continue
                score -= dist
            if best is None or score > best[0]:
                best = (score, k)
        if best is None:
            out.append(None)
            continue
        k = best[1]
        ys, xs = np.nonzero(lab == k)
        pts = np.stack([xs, ys], 1).astype(np.float32)
        cx, cy = xs.mean(), ys.mean()
        ell = None
        if len(pts) >= 5:
            cnts, _ = cv2.findContours((lab == k).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            c0 = max(cnts, key=cv2.contourArea)
            if len(c0) >= 5:
                ell = cv2.fitEllipse(c0)
        x, y, w, h, a = st[k]
        rec = dict(i=i, cx=float(cx), cy=float(cy), area=int(a), w=int(w), h=int(h))
        if ell is not None:
            rec.update(ex=ell[0][0], ey=ell[0][1], emaj=max(ell[1]), emin=min(ell[1]), eang=ell[2])
        out.append(rec)
        prev = (cx, cy)
    return out


if __name__ == '__main__':
    res = {}
    for s in ['', 's', 'x']:
        res[s or 'a'] = track(s)
    json.dump(res, open('tracks.json', 'w'), indent=1)
    for s in res:
        print('==', s)
        for r in res[s]:
            if r is None:
                print('None'); continue
            print('%2d %7.1f %7.1f a=%4d w=%3d h=%3d emaj=%5.1f emin=%5.1f ang=%5.1f' % (
                r['i'], r['cx'], r['cy'], r['area'], r['w'], r['h'], r.get('emaj', 0), r.get('emin', 0), r.get('eang', 0)))
