"""Ball centre/diameter in the o render: threshold whiteness halfway between ball and local background, fit min-enclosing circle
and an ellipse to the upper/left/right boundary (the lower boundary touches the shadow)."""
import cv2, numpy as np, json
B = '/home/user/quantiphy-challenge/research/next/labaudit/0039'
S = '/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
trk = json.load(open(f'{B}/track.json'))
out = {}
for r in ['0039', '0039s']:
    fr = np.load(f'{S}/fr_{r}.npy')
    out[r] = {}
    for i in range(19, 42):
        t = trk[r].get(str(i))
        if t is None: continue
        cx, cy = t['e']
        x0, y0 = int(cx) - 40, int(cy) - 40
        crop = fr[i, y0:y0 + 80, x0:x0 + 80].astype(float)
        hsv = cv2.cvtColor(fr[i, y0:y0 + 80, x0:x0 + 80], cv2.COLOR_BGR2HSV).astype(float)
        wh = hsv[..., 2] - 1.5 * hsv[..., 1]  # whiteness
        ball = np.percentile(wh, 97); bgv = np.median(wh)
        m = (wh > (ball + bgv) / 2).astype(np.uint8)
        n, lab, st, cen = cv2.connectedComponentsWithStats(m)
        k = 1 + np.argmax(st[1:, 4]); blob = (lab == k).astype(np.uint8)
        cnts, _ = cv2.findContours(blob, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        c = max(cnts, key=cv2.contourArea)
        (ex, ey), (a1, a2), ang = cv2.fitEllipse(c)
        ys, xs = np.nonzero(blob)
        w = xs.max() - xs.min() + 1; h = ys.max() - ys.min() + 1
        out[r][i] = dict(c=[ex + x0, ey + y0], axes=[min(a1, a2), max(a1, a2)], w=int(w), h=int(h), top=int(ys.min() + y0), bot=int(ys.max() + y0),
                         l=int(xs.min() + x0), rr=int(xs.max() + x0))
        o = out[r][i]
        print(r, i, 'centre %.1f %.1f' % tuple(o['c']), 'axes %.1f %.1f' % tuple(o['axes']), 'w h', w, h, 'x', o['l'], o['rr'], 'y', o['top'], o['bot'])
json.dump(out, open(f'{B}/ballfit.json', 'w'), indent=1)
