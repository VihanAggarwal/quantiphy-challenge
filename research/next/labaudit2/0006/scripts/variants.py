"""Cross-check of the label-style v(1.2 s) with other click-centre choices and the Z-depth reading of depth_info."""
import numpy as np
from common import F, CX, CY, ray
R25, R30 = 1.402, 1.065
cents = {'silhouette (bg-diff/s outline)': ((580.5, 224.0), (571.0, 283.0)),
         'yellow-only hull': ((589.3, 223.6), (567.1, 278.3)),
         'bbox centre o thr25': ((580.0, 224.0), (571.0, 285.0)),
         's render thr25 centroid': ((580.9, 221.8), (570.9, 280.5))}
for name, (a, b) in cents.items():
    for R31 in (0.990, 0.998, 1.010):
        vr = 25 * np.linalg.norm(R31 * ray(*b) - R30 * ray(*a))
        Zp = lambda c, Z: np.array([(c[0] - CX) * Z / F, (c[1] - CY) * Z / F, Z])
        Z31 = R30 + (R30 - R25) / 5 + (R31 - 0.998)
        vz = 25 * np.linalg.norm(Zp(b, Z31) - Zp(a, R30))
        print('%-32s R31 %.3f: range model %.2f m/s | Z-depth model %.2f m/s' % (name, R31, vr, vz))
# vertical-only free fall speed at 1.2 s for apex 0.99-1.0 s (what 2.1 corresponds to)
for ta in (0.985, 0.99, 0.995, 1.0):
    print('g*(1.2-%.3f) = %.2f m/s' % (ta, 9.8 * (1.2 - ta)))
