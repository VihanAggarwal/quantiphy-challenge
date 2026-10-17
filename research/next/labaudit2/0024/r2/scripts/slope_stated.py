import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from geom import *
def lerp(a, b, t): return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
def bp(p, r): return ray(*p) * r
# top edge: TL(751,360)-TR(857,361) ; bottom edge BL(609,467)-BR(705,493). t=0 at the left end
print('label-style slope length with stated far 1.243 / near 0.990 for click pairs (top t, bottom t):')
for tt in [0, 0.25, 0.5]:
    for tb in [0, 0.25, 0.5]:
        pf = lerp(TLp, TRp, tt); pn = lerp(BLp, BRp, tb)
        Xf = on_slope(*pf); Xn = on_slope(*pn)
        print('  top %.2f bot %.2f: stated %.1f | model %.1f | model ranges %.3f / %.3f' % (tt, tb, np.linalg.norm(bp(pf, 1.243) - bp(pn, 0.990)) * 100,
              np.linalg.norm(Xf - Xn) * 100, np.linalg.norm(Xf), np.linalg.norm(Xn)))
