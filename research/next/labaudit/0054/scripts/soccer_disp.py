"""Soccer displacement 1.0 -> 1.4 s. Capture-time mapping: video n=24 -> 1.00 s, n=33 -> 1.36 s, n=34 -> 1.40 s.
b: rest/1.0 s centre ~(915,617) (~65 px, partly hidden by the person), 1.4 s = bx n34 (884.5,488.9) minor 55.7 major 61.8.
Ranges from size with D = 0.20 m (19-21 cm bracket), and the 2.0 s anchor (n48, stated 3.254 m, 44-47 px) as a scale check."""
import numpy as np
F, CX, CY = 711.0, 640.0, 360.0
def ray(u, v):
    d = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return d / np.linalg.norm(d)
def srange(u, v, dpx, D):
    th = np.arctan(np.hypot(u - CX, v - CY) / F); b = dpx / 2; s = b * np.cos(th) / np.sqrt(F ** 2 + b ** 2); return D / 2 / s
for D in (0.19, 0.20, 0.21):
    for d24 in (62, 65, 68):
        for (n, uv, dpx) in ((33, (889.2, 498.9), 55.8), (34, (884.5, 488.9), 55.7), (35, (881.6, 479.5), 54.3)):
            r24 = srange(915, 617, d24, D); rn = srange(*uv, dpx, D)
            print('D %.2f d24 %d: r24 %.3f | n%d r %.3f disp %.3f' % (D, d24, r24, n, rn, np.linalg.norm(rn * ray(*uv) - r24 * ray(915, 617))))
# check: 2.0 s anchor -> what D makes the size range equal 3.254 (+R)?
for dpx in (44, 45.5, 47):
    print('n48 %.1f px: D for range 3.254 = %.3f, for 3.354 = %.3f' % (dpx, 0.2 * 3.254 / srange(834.2, 370.8, dpx, 0.2), 0.2 * 3.354 / srange(834.2, 370.8, dpx, 0.2)))
# b with the stated 3.254 m at n48 as the scale, ranges by size ratio
r48 = 3.254 + 0.10
for d24 in (62, 65, 68):
    r24 = r48 * 45.5 / d24 * (np.cos(np.arctan(np.hypot(915 - CX, 617 - CY) / F)) / np.cos(np.arctan(np.hypot(834.2 - CX, 370.8 - CY) / F)))
    r34 = r48 * 45.5 / 55.7 * (np.cos(np.arctan(np.hypot(884.5 - CX, 488.9 - CY) / F)) / np.cos(np.arctan(np.hypot(834.2 - CX, 370.8 - CY) / F)))
    print('anchor-scaled d24 %d: r24 %.3f r34 %.3f disp %.3f' % (d24, r24, r34, np.linalg.norm(r34 * ray(884.5, 488.9) - r24 * ray(915, 617))))
