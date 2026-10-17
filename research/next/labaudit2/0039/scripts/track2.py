"""Whiteness tracker for the ping-pong ball (o and s renders; x render too).
mask = V > vthr & S < sthr inside a window; largest blob, holes filled; circle fit to boundary points
above the blob's lower 25 % (bottom of the ball is shaded / shadowed).  Reports centre (circle fit),
bbox-mid centre, widest-row width."""
import cv2, numpy as np, json, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0039/scripts')
from frames import load
OUT = '/home/user/quantiphy-challenge/research/next/labaudit2/0039'
def circfit(x, y):
    A = np.c_[2 * x, 2 * y, np.ones_like(x)]; b = x ** 2 + y ** 2
    c, *_ = np.linalg.lstsq(A, b, rcond=None); r = np.sqrt(c[2] + c[0] ** 2 + c[1] ** 2)
    return float(c[0]), float(c[1]), float(r)
def track(r, vthr=165, sthr=60, frames=range(14, 42)):
    fr = load(r)
    out = {}
    px, py = 565, 441
    for i in frames:
        x0, y0 = int(px) - 45, int(py) - 40
        roi = fr[i, y0:y0 + 95, x0:x0 + 90]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        m = ((hsv[..., 2] > vthr) & (hsv[..., 1] < sthr)).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(m)
        if n < 2: continue
        k = 1 + np.argmax(st[1:, 4]); blob = (lab == k).astype(np.uint8)
        cnts, _ = cv2.findContours(blob, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        c = max(cnts, key=cv2.contourArea)
        blob = np.zeros_like(blob); cv2.drawContours(blob, [c], -1, 1, -1)
        c = c[:, 0, :].astype(float)
        ys, xs = np.nonzero(blob)
        top, bot = ys.min(), ys.max()
        sel = c[c[:, 1] <= top + 0.75 * (bot - top)]
        cx, cy, rad = circfit(sel[:, 0], sel[:, 1])
        rowsw = blob.sum(1); wmax = rowsw.max()
        l, rr = xs.min(), xs.max()
        out[i] = dict(cf=[cx + x0, cy + y0, rad], bb=[(l + rr) / 2 + x0, (top + bot) / 2 + y0], w=int(rr - l + 1), h=int(bot - top + 1),
                      wmax=int(wmax), area=int(blob.sum()), top=int(top + y0), bot=int(bot + y0), l=int(l + x0), rr=int(rr + x0))
        px, py = cx + x0, cy + y0
    return out
if __name__ == '__main__':
    res = {}
    for r in ['0039', '0039s', '0039x']:
        res[r] = track(r)
        prev = None
        for i in sorted(res[r]):
            o = res[r][i]
            st = '' if prev is None else 'step %.1f %.1f' % (o['cf'][0] - prev[0], o['cf'][1] - prev[1])
            print(r, i, 'cf %.1f %.1f r%.1f' % tuple(o['cf']), 'bb %.1f %.1f' % tuple(o['bb']), 'w', o['w'], 'h', o['h'], 'area', o['area'], st)
            prev = o['cf']
    json.dump(res, open(f'{OUT}/track2.json', 'w'), indent=1)
