"""Static sizes in 0039, two routes.
Route A: pixel endpoints back-projected with the stated (ToF) range of the object (label-like).
Route B: table plane from table.py (h = camera height above table from 76.0 x 60.3 rectification), base on the plane,
         top along the plane normal; widths at the object's axis depth."""
import numpy as np
F, CX, CY = 711.0, 640.0, 360.0
pl = np.load('/home/user/quantiphy-challenge/research/next/labaudit/0039/plane.npy'); n, d0 = pl[:3], pl[3]
def ray(u, v):
    r = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return r / np.linalg.norm(r)
def P(u, v, rng): return rng * ray(u, v)
def on(u, v, h): r = ray(u, v); return h / (n @ r) * r
def up_to(base, u, v):
    a = -n; r = ray(u, v)   # -n points up (n points down toward the table)
    A = np.array([[a @ a, -a @ r], [a @ r, -r @ r]]); b = np.array([-(base @ a), -(base @ r)])
    hh, s = np.linalg.solve(A, b); return base + hh * a, hh
# pixel readings (zooms z_*.png, row edge scans)
bot = dict(top=(664, 329.8), bot=(664, 477.5), L=(640.5, 380), R=(687.5, 380), rng=0.9998)
cup = dict(top=(759.3, 375.0), bot=(757.5, 498.0), L=(724.0, 381), R=(794.5, 381), rng=0.874)
pok = dict(top=(686, 416.7), botL=(668, 495.5), botR=(694, 500.5), rng=0.9035)
print('Route A (stated range)')
for nm, o in [('bottle', bot), ('cup', cup)]:
    print(f'  {nm} height {np.linalg.norm(P(*o["top"], o["rng"]) - P(*o["bot"], o["rng"]))*100:.2f}  width {np.linalg.norm(P(*o["L"], o["rng"]) - P(*o["R"], o["rng"]))*100:.2f}')
for rr in (0.0, 0.035, 0.044):
    print(f'  cup rim at range+{rr:.3f}: {np.linalg.norm(P(*cup["L"], cup["rng"]+rr) - P(*cup["R"], cup["rng"]+rr))*100:.2f}')
print(f'  poker height (feet avg {(495.5+500.5)/2}) {np.linalg.norm(P(686,416.7,pok["rng"]) - P(686,498,pok["rng"]))*100:.2f}')
for h in (d0, 0.169, 0.1766):
    print(f'Route B h={h:.4f}')
    bb = on(*bot['bot'], h); _, H = up_to(bb, *bot['top'])
    ax = bb + 0.034 * bb / np.linalg.norm(bb) * 0   # front point
    zc = (bb * (np.linalg.norm(bb) + 0.024) / np.linalg.norm(bb))[2]
    print(f'  bottle base-front range {np.linalg.norm(bb):.4f}  height {H*100:.2f}  diam(axis Z) {(bot["R"][0]-bot["L"][0])/F*zc*100:.2f}')
    cb = on(*cup['bot'], h); _, H = up_to(cb, *cup['top'])
    zc = (cb * (np.linalg.norm(cb) + 0.040) / np.linalg.norm(cb))[2]
    print(f'  cup base-front range {np.linalg.norm(cb):.4f}  height {H*100:.2f}  rim diam(axis Z) {(cup["R"][0]-cup["L"][0])/F*zc*100:.2f}')
    pb = on(686, 498, h); _, H = up_to(pb, *pok['top'])
    print(f'  poker base range {np.linalg.norm(pb):.4f} height {H*100:.2f}')
