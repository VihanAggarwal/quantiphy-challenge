"""Diameters of the green (tennis) and white balls from ellipse minor axes + ranges.
Ranges: (i) ballistic fit (scale from g) in that camera; (ii) the same fit's range profile rescaled to the stated
range at 1.0 s (a: green 3.039, white 3.0735; b: green 1.331, white 1.235)."""
import numpy as np, sys, os, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ballistic_a as BA, ballistic_b as BB
from ballistic_a import tc
from small_sizes import masks, ell
D = '/home/user/quantiphy-challenge/research/next/labaudit/0054/frames/'
F, CX, CY = 711.0, 640.0, 360.0
def s_of(u, v, minor):
    th = np.arctan(np.hypot(u - CX, v - CY) / F); b = minor / 2; return b * np.cos(th) / np.sqrt(F ** 2 + b ** 2)
def measure(render, frames, box_fn):
    out = {}
    for n in frames:
        f = cv2.imread(D + '%s_%02d.png' % (render, n)); yel, wh = masks(f, render)
        yd = cv2.dilate(yel.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
        for k in ('G', 'W'):
            box = box_fn(n, k)
            if box is None: continue
            e = ell(yel if k == 'G' else (wh & ~yd), box)
            if e: out[(n, k)] = e
    return out
# camera b
ob = BB.fit_joint([BB.green, BB.white], [list(range(25, 36)), [21, 22, 23] + list(range(25, 36))], pitch=29.9, roll=-6.5)
bG, bW = ob['balls']
def boxb(n, k):
    tr = BB.green if k == 'G' else BB.white
    if n not in tr: return None
    u, v = tr[n]; return (int(u - 40), int(v - 40), int(u + 40), int(v + 40))
mb = measure('bx', range(26, 34), boxb)
print('camera b (fit ranges at 1.0: G %.3f W %.3f; stated G 1.331 W 1.235)' % (np.linalg.norm(bG['pos'](1.0)), np.linalg.norm(bW['pos'](1.0))))
for (n, k), e in sorted(mb.items()):
    ball = bG if k == 'G' else bW; st = 1.331 if k == 'G' else 1.235
    r = np.linalg.norm(ball['pos'](tc(n))); r_st = r * st / np.linalg.norm(ball['pos'](1.0))
    s = s_of(e[0], e[1], e[2])
    print('b n%2d %s minor %.1f  range_fit %.3f -> D %.1f cm | range_stated-scaled %.3f -> D %.1f cm' % (n, k, e[2], r, 2 * r * s * 100, r_st, 2 * r_st * s * 100))
# camera a
oaG = BA.fit(BA.green, list(range(24, 36)), 2.5); oaW = BA.fit(BA.white, list(range(29, 36)), 2.5)
def boxa(n, k):
    tr = BA.green if k == 'G' else BA.white
    if n not in tr: return None
    u, v = tr[n]; return (int(u - 30), int(v - 30), int(u + 30), int(v + 30))
ma = measure('ax', range(25, 36), boxa)
for (n, k), e in sorted(ma.items()):
    o = oaG if k == 'G' else oaW; st = 3.039 if k == 'G' else 3.0735
    r = np.linalg.norm(o['pos'](tc(n))); r_st = r * st / np.linalg.norm(o['pos'](1.0))
    s = s_of(e[0], e[1], e[2])
    print('a n%2d %s minor %.1f  range_fit %.3f -> D %.1f cm | range_stated-scaled %.3f -> D %.1f cm' % (n, k, e[2], r, 2 * r * s * 100, r_st, 2 * r_st * s * 100))
