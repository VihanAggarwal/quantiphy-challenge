"""Orange ball (basketball, 23.2 cm stated in 0035) displacement 0.5 -> 1.0 s, routes:
 a1: label emulation in a: stated ranges along rays through the mask centres (video frames 12 and 24)
 a2: a, ranges from apparent size (minor axis model) at frames 12/24 (24 is cut by the bottom edge -> use width)
 b1: b, stated 0.5 s range (2.24) + size-scaled range at 1.0 s (size ratio), rays through b centres
 b2: b, both ranges from apparent size."""
import numpy as np
F, CX, CY = 711.0, 640.0, 360.0
R = 0.116
def ray(u, v):
    d = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return d / np.linalg.norm(d)
def P(u, v, r): return r * ray(u, v)
def size_range(u, v, dpx, Rb=R):
    th = np.arctan(np.hypot(u - CX, v - CY) / F)
    b = dpx / 2.0
    s = b * np.cos(th) / np.sqrt(F ** 2 + b ** 2)
    return Rb / s
a12, a24 = (343.7, 605.0), (584.8, 678.8)
b12, b24 = (716.6, 536.1), (537.8, 385.5)
out = {}
out['a1_stated'] = np.linalg.norm(P(*a12, 2.3557) - P(*a24, 1.81))
out['a1_stated+R'] = np.linalg.norm(P(*a12, 2.3557 + R) - P(*a24, 1.81 + R))
# a size: frame 12 h=74 (vertical, little blur), frame 24 width 92 includes blur; use frame 23 h=94 radial -> scale to 24 by track
ra12 = size_range(*a12, 74.0); ra23 = size_range(560.0, 671.8, 90.0)
out['a_size_ranges(12,23)'] = (ra12, ra23)
out['b_size_ranges(12,24)'] = (size_range(*b12, 77.0), size_range(*b24, 61.0))
rb12, rb24 = out['b_size_ranges(12,24)']
out['b1_stated0.5+sizeRatio'] = np.linalg.norm(P(*b12, 2.24) - P(*b24, 2.24 * rb24 / rb12))
out['b2_size'] = np.linalg.norm(P(*b12, rb12) - P(*b24, rb24))
out['b_copied_1.81 (current b geometry)'] = np.linalg.norm(P(*b12, 2.24) - P(*b24, 1.81))
for k, v in out.items(): print(k, np.round(v, 4))
