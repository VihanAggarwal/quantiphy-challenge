"""Orange-soccer centre distance at 1.0 s (frame 24); soccer has just started to move (rest position until n~23).
D1 camera a: orange (584.8,678.8) stated 1.81 (+R for centre); soccer centre ~(153,598), 65 px wide -> range from size (D 19-21 cm)
   and from the floor plane (H 0.95, pitch 1-3.8 deg).
D2 camera b: orange (537.8,385.5), range from size (61 px) / stated-0.5s-scaled; soccer centre ~(915,617), ~65 px tall."""
import numpy as np
F, CX, CY = 711.0, 640.0, 360.0
def ray(u, v):
    d = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return d / np.linalg.norm(d)
def srange(u, v, dpx, D):
    th = np.arctan(np.hypot(u - CX, v - CY) / F); b = dpx / 2; s = b * np.cos(th) / np.sqrt(F ** 2 + b ** 2); return D / 2 / s
def on_plane(u, v, H, pitch, hgt):
    p = np.radians(pitch); n = np.array([0, np.cos(p), np.sin(p)]); d = ray(u, v); return (H - hgt) / (n @ d)
O_a = (584.8, 678.8); S_a = (153.0, 598.0)
print('camera a:')
for ro, lab in ((1.81, 'stated'), (1.81 + 0.116, 'stated+R')):
    for D in (0.19, 0.20, 0.21):
        rs = srange(*S_a, 65, D)
        print('  orange %s %.3f, soccer size-range(D=%.2f) %.3f -> dist %.3f | soccer front-surface %.3f -> %.3f' % (
            lab, ro, D, rs, np.linalg.norm(ro * ray(*O_a) - rs * ray(*S_a)), rs - D / 2,
            np.linalg.norm(ro * ray(*O_a) - (rs - D / 2) * ray(*S_a))))
    for pitch in (1.0, 2.5, 3.8):
        rs = on_plane(*S_a, 0.95, pitch, 0.10)
        print('  orange %s, soccer floor-range (pitch %.1f) %.3f -> dist %.3f' % (lab, pitch, rs, np.linalg.norm(ro * ray(*O_a) - rs * ray(*S_a))))
print('camera b:')
O_b = (537.8, 385.5); S_b = (915.0, 617.0)
for ro in (srange(*O_b, 61, 0.232), 2.24 * 2.7362 / 2.2222, 2.24 * 2.7362 / 2.2222 + 0.116):
    for D in (0.19, 0.20, 0.21):
        for dpx in (62, 65, 68):
            rs = srange(*S_b, dpx, D)
            print('  orange %.3f soccer(D %.2f, %d px) %.3f -> dist %.3f' % (ro, D, dpx, rs, np.linalg.norm(ro * ray(*O_b) - rs * ray(*S_b))))
