"""Static sizes, two routes.
Route A: pixel endpoints back-projected with the stated range (cup range typo 8420 m -> 0.842 m).
Route B: table plane (rectified 76.0 x 60.3; s=1 geometric, s=1.05 = ToF/geo ratio seen on the credit card and poker tower),
         base on the plane, top along the plane normal; widths at the object's axis depth."""
import numpy as np
F, CX, CY = 711.0, 640.0, 360.0
pl = np.load('/home/user/quantiphy-challenge/research/next/labaudit/0040/plane.npy'); n, d0 = pl[:3], pl[3]
def ray(u, v):
    r = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return r / np.linalg.norm(r)
def P(u, v, r): return r * ray(u, v)
def on(u, v, s): r = ray(u, v); return s * d0 / (n @ r) * r
def up_to(base, u, v):
    # point on line base + h*(-n) closest to the ray through (u,v)
    a = -n; r = ray(u, v)
    A = np.array([[a @ a, -a @ r], [a @ r, -r @ r]]); b = np.array([-(base @ a), -(base @ r)])
    h, s = np.linalg.solve(A, b); return base + h * a, h
rows = {}
# pixel measurements read from the zoomed x-render median (zoom_*.png)
cup = dict(top=(776, 376.5), bot=(776, 504.5), L=(740, 379), R=(813, 379), rng=0.842)
pok = dict(top=(684, 416), bot=(692, 499), rng=0.91)
tape = dict(L=(551, 460), R=(629.5, 460), bot=(590, 484), rng=0.973)
print('Route A (stated range)')
print('  cup height   %.2f' % (np.linalg.norm(P(*cup['top'], cup['rng']) - P(*cup['bot'], cup['rng'])) * 100))
print('  cup rim diam %.2f  (at range+3.6cm silhouette depth: %.2f)' % (np.linalg.norm(P(*cup['L'], cup['rng']) - P(*cup['R'], cup['rng'])) * 100,
      np.linalg.norm(P(*cup['L'], cup['rng'] + .036) - P(*cup['R'], cup['rng'] + .036)) * 100))
print('  poker height %.2f' % (np.linalg.norm(P(*pok['top'], pok['rng']) - P(*pok['bot'], pok['rng'])) * 100))
print('  tape diam    %.2f  (at range+4.5cm silhouette depth: %.2f)' % (np.linalg.norm(P(*tape['L'], tape['rng']) - P(*tape['R'], tape['rng'])) * 100,
      np.linalg.norm(P(*tape['L'], tape['rng'] + .045) - P(*tape['R'], tape['rng'] + .045)) * 100))
for s in (1.0, 1.05):
    print(f'Route B (table plane, s={s})')
    # cup: bottom-front pixel is on the plane at the front surface; axis is ~radius behind
    bf = on(*cup['bot'], s); _, h = up_to(bf, *cup['top']); print(f'  cup height   {h*100:.2f}  (base range {np.linalg.norm(bf):.3f})')
    axis = bf * (np.linalg.norm(bf) + 0.042) / np.linalg.norm(bf)
    zc = axis[2]
    w = np.linalg.norm(np.array([(cup['L'][0] - CX) / F * zc, 0, 0]) - np.array([(cup['R'][0] - CX) / F * zc, 0, 0]))
    print(f'  cup rim diam {w*100:.2f}  (axis Z {zc:.3f})')
    b = on(*pok['bot'], s); _, h = up_to(b, *pok['top']); print(f'  poker height {h*100:.2f}  (base range {np.linalg.norm(b):.3f})')
    tb = on(*tape['bot'], s); zc = (tb * (np.linalg.norm(tb) + 0.05) / np.linalg.norm(tb))[2]
    print(f'  tape diam    {(tape["R"][0]-tape["L"][0]) / F * zc * 100:.2f}  (front-base range {np.linalg.norm(tb):.3f})')
