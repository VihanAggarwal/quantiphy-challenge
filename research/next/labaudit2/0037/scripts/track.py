"""Ping-pong ball blob per video frame, per render. Background = per-pixel median over all 49 frames.
Writes track.json: {render: {frame: {u,v (centroid), bx0,by0,bx1,by1, area, emaj, emin, eang, eu, ev}}}."""
import json, sys, cv2, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0037/scripts')
from common import frames, OUT

res = {}
for r in ('x', '', 's'):
    fr = frames(r)
    st = np.stack(fr).astype(np.float32)
    med = np.median(st, axis=0)
    out = {}
    prev = None
    for i, f in enumerate(fr):
        d = np.abs(f.astype(np.float32) - med).sum(2)
        hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
        m = ((d > 60) & (hsv[..., 2] > 130) & (hsv[..., 1] < 90)).astype(np.uint8)
        m[:150] = 0; m[620:] = 0; m[:, 1000:] = 0
        if r == '':  # person region (blurred jeans/arm) is excluded by colour mostly; keep left of x=1000
            pass
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        n, lab, sts, cen = cv2.connectedComponentsWithStats(m)
        if n < 2:
            continue
        cand = []
        for k in range(1, n):
            x, y, w, h, a = sts[k]
            if a < 40 or w > 70 or h > 70:
                continue
            dist = 0 if prev is None else np.hypot(cen[k][0] - prev[0], cen[k][1] - prev[1])
            cand.append((dist if prev is not None else -a, k))
        if not cand:
            continue
        cand.sort()
        k = cand[0][1]
        x, y, w, h, a = sts[k]
        cs, _ = cv2.findContours((lab == k).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        c = max(cs, key=cv2.contourArea)
        e = cv2.fitEllipse(c) if len(c) >= 5 else ((cen[k][0], cen[k][1]), (w, h), 0)
        out[i] = dict(u=round(float(cen[k][0]), 2), v=round(float(cen[k][1]), 2), bx0=int(x), by0=int(y), bx1=int(x + w - 1),
                      by1=int(y + h - 1), area=int(a), eu=round(e[0][0], 2), ev=round(e[0][1], 2),
                      emaj=round(max(e[1]), 2), emin=round(min(e[1]), 2), eang=round(e[2], 1))
        prev = (cen[k][0], cen[k][1])
    res[r or 'o'] = out
    print('render', r or 'o')
    for i in sorted(out):
        o = out[i]
        print('%2d u=%7.2f v=%7.2f bbox=(%d,%d)-(%d,%d) w=%d h=%d a=%d ell=(%.1f,%.1f) maj=%.1f min=%.1f ang=%.0f' % (
            i, o['u'], o['v'], o['bx0'], o['by0'], o['bx1'], o['by1'], o['bx1'] - o['bx0'] + 1, o['by1'] - o['by0'] + 1,
            o['area'], o['eu'], o['ev'], o['emaj'], o['emin'], o['eang']))
json.dump(res, open(OUT + '/track.json', 'w'), indent=0)
