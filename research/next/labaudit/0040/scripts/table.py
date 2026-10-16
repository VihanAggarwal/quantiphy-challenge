"""Fit table-top edges in the x-render median, rectify with known size, recover the plane."""
import cv2, numpy as np
B = '/home/user/quantiphy-challenge/research/next/labaudit/0040'
F, CX, CY = 711.0, 640.0, 360.0
m = cv2.imread(f'{B}/median_x.png')
g = m.astype(int).sum(-1)
mask = (g > 40).astype(np.uint8); mask[690:] = 0
n, lab, st, cen = cv2.connectedComponentsWithStats(mask)
k = 1 + np.argmax(st[1:, 4]); mask = (lab == k)
top = {x: np.nonzero(mask[:640, x])[0].min() for x in range(212, 1140)}
bot = {}
def fit(xs):
    xs = np.array(xs); ys = np.array([top[x] for x in xs], float)
    p = np.polyfit(xs, ys, 1)
    r = ys - np.polyval(p, xs)
    keep = np.abs(r) < 1.5
    p = np.polyfit(xs[keep], ys[keep], 1)
    return p
L = fit(range(225, 440))
Bk = fit(list(range(830, 905)) + list(range(470, 478)))
R = fit(range(935, 1130))
# front edge: the top-surface front line = upper boundary of the wood edge band; find it by colour change
# use left-most and right-most column extents as front corners
def inter(p, q):
    x = (q[1] - p[1]) / (p[0] - q[0]); return np.array([x, np.polyval(p, x)])
BL = inter(L, Bk); BR = inter(Bk, R)
print('left', L, 'back', Bk, 'right', R)
print('BL', BL, 'BR', BR)
