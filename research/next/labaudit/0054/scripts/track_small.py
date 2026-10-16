"""Track the green (tennis) ball and the white/pink ball in 0054ax (green screen) and 0054bx (black bg)."""
import cv2, numpy as np, sys, json
D = '/home/user/quantiphy-challenge/research/next/labaudit/0054/frames/'
def comps(m, minarea=15):
    n, lab, st, cen = cv2.connectedComponentsWithStats(m.astype(np.uint8), 8)
    out = []
    for k in range(1, n):
        a = st[k, cv2.CC_STAT_AREA]
        if a < minarea: continue
        ys, xs = np.nonzero(lab == k)
        out.append(dict(cx=float(xs.mean()), cy=float(ys.mean()), area=int(a), w=int(st[k, 2]), h=int(st[k, 3]),
                        x0=int(st[k, 0]), y0=int(st[k, 1])))
    return sorted(out, key=lambda d: -d['area'])
def masks(im, render):
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(int)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    b, g, r = [im[..., k].astype(int) for k in range(3)]
    if render == 'ax':
        bg = (g > 200) & (r < 80) & (b < 80)
    else:
        bg = (v < 40)
    yellow = (~bg) & (h >= 20) & (h <= 42) & (s > 90) & (v > 90)
    white = (~bg) & (s < 70) & (v > 120)
    return yellow, white
if __name__ == '__main__':
    render = sys.argv[1]
    x0, x1, y0, y1 = [int(a) for a in sys.argv[2:6]]
    for i in range(int(sys.argv[6]), int(sys.argv[7])):
        im = cv2.imread(D + '%s_%02d.png' % (render, i))
        yel, wh = masks(im, render)
        sub = np.zeros_like(yel); sub[y0:y1, x0:x1] = True
        cy = comps(yel & sub); cw = comps(wh & sub)
        fmt = lambda L: ' '.join('(%.1f,%.1f a%d %dx%d)' % (d['cx'], d['cy'], d['area'], d['w'], d['h']) for d in L[:3])
        print('%2d Y: %s | W: %s' % (i, fmt(cy), fmt(cw)))
