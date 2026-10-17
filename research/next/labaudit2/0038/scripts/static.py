"""Static rows, route A: endpoints back-projected at the stated range; route B: table plane (height above a base
point on the plane; widths at the base's plane depth / axis depth). Pixel reads from z_objs.png / z_poker.png
(x-render median)."""
import numpy as np, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0038/scripts')
from common import B, F, ray
pl = np.load(f'{B}/plane.npy'); n, h0 = pl[:3], pl[3]
def A(p, q, r1, r2=None):
    return np.linalg.norm(ray(*p) * r1 - ray(*q) * (r2 if r2 else r1)) * 100
def base(p, h):           # point on the table plane under pixel p
    d = ray(*p); return d * h / (n @ d)
def height(pb, pt, h):    # vertical height above plane point under pb, top pixel pt
    Xb = base(pb, h); d = ray(*pt)
    # closest point on the top ray to the vertical line Xb + s*(-n) (n points from table to camera side? sign test)
    up = -n if (n @ (Xb + 0.1 * -n)) < (n @ Xb) else n
    # solve Xb + s*up = t*d (least squares)
    M = np.c_[up, -d]; s, t = np.linalg.lstsq(M, -Xb, rcond=None)[0]
    return abs(s) * 100, np.linalg.norm(Xb)
for h in (h0, 0.1728):
    print(f'--- plane h={h:.4f}')
    # bottle: top (665,330.5) bottom-front (665,478.5)
    hb, rb = height((665, 478.5), (665, 330.5), h); print(f'bottle height: A {A((665,330.5),(665,478.5),0.9998):.2f}  B {hb:.2f} (base range {rb:.3f}, stated 0.9998)')
    hp, rp = height((690, 499.5), (690, 417), h); hp2, rp2 = height((672, 495), (690, 417), h)
    print(f'poker height: A {A((690,417),(690,499.5),0.9035):.2f} / back foot {A((690,417),(672,495),0.9035):.2f}  B {hp:.2f} / {hp2:.2f} (base ranges {rp:.3f} {rp2:.3f}, stated 0.9035)')
    # cup rim: edges 723.5 and 794.5 at row 377; front-base (759, 497.5)
    Xc = base((759, 497.5), h); rc = np.linalg.norm(Xc)
    print(f'cup rim: A front {A((723.5,377),(794.5,377),0.874):.2f}  A axis(+4.3) {A((723.5,377),(794.5,377),0.874+0.043):.2f}  '
          f'B base-front range {rc:.3f} -> rim at {A((723.5,377),(794.5,377),rc):.2f} / axis {A((723.5,377),(794.5,377),rc+0.043):.2f}')
    # cup-bottle centre to centre: centre clicks bottle (665, 404), cup (759, 436)
    print(f'cup-bottle: A clicks at stated ranges {A((665,404),(759,436),0.9998,0.874):.2f}; '
          f'B axis-to-axis on the plane {np.linalg.norm((base((759,497.5),h)) - base((665,478.5),h) + 0*n)*100:.2f} (front-base points; '
          f'axes {np.linalg.norm(base((759,497.5),h)*(1+0.043/np.linalg.norm(base((759,497.5),h))) - base((665,478.5),h)*(1+0.033/np.linalg.norm(base((665,478.5),h))))*100:.2f})')
