"""Cup - bottle centre distance. Route A: centre pixels + stated ranges. Route B: axes on the table plane."""
import numpy as np
F, CX, CY = 711.0, 640.0, 360.0
pl = np.load('/home/user/quantiphy-challenge/research/next/labaudit/0039/plane.npy'); n, d0 = pl[:3], pl[3]
def ray(u, v):
    r = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return r / np.linalg.norm(r)
def on(u, v, h): r = ray(u, v); return h / (n @ r) * r
print('Route A: centre pixels with stated ranges')
for bc, cc in [((664, 403.7), (759.3, 436.5)), ((664, 380), (759.3, 420)), ((664, 430), (759.3, 460)), ((660, 403), (755, 436))]:
    pb = 0.9998 * ray(*bc); pc = 0.874 * ray(*cc)
    print(f'  bottle px {bc} cup px {cc}: {np.linalg.norm(pb-pc)*100:.2f}  (horiz-only {np.linalg.norm((pb-pc) - ((pb-pc)@n)*n)*100:.2f})')
print('Route B: base-front points on the plane, pushed back along the horizontal view direction by the radius')
for h in (d0, 0.169, 0.1766):
    bb = on(664, 477.5, h); cb = on(757.5, 498.0, h)
    def back(p, r):
        v = p - (p @ n) * n; v /= np.linalg.norm(v); return p + r * v
    for rb, rc in [(0, 0), (0.0335, 0.033), (0.0335, 0.040)]:
        A = back(bb, rb); C = back(cb, rc)
        print(f'  h={h:.4f} rb={rb} rc={rc}: axis distance {np.linalg.norm(A-C)*100:.2f}  ranges {np.linalg.norm(A):.3f} {np.linalg.norm(C):.3f}')
