"""Route B: table plane (front edge = 60.3 cm side, as in family 0002; 76 cm alternative printed too).
Contact points of the toy on the table -> Z; toy extents -> size. Route C: fall parabola -> Z from g."""
import numpy as np
D = '/home/user/quantiphy-challenge/research/next/labaudit/0006/'
C = np.load(D + 'scripts/corners.npy')  # BL BR FR FL
f, cx, cy = 711.0, 640.0, 360.0
def ray(u, v): return np.array([u - cx, v - cy, f])
def line(p, q): return np.cross(np.r_[p, 1], np.r_[q, 1])
v1 = np.cross(line(C[3], C[0]), line(C[2], C[1])); v2 = np.cross(line(C[0], C[1]), line(C[3], C[2]))
d1 = np.array([v1[0] - cx * v1[2], v1[1] - cy * v1[2], f * v1[2]]); d1 /= np.linalg.norm(d1)
d2 = np.array([v2[0] - cx * v2[2], v2[1] - cy * v2[2], f * v2[2]]); d2 /= np.linalg.norm(d2)
n = np.cross(d1, d2); n /= np.linalg.norm(n); n = n if n[1] < 0 else -n   # up normal (camera y down)
print('VP depth dir pixel (%.1f, %.1f); normal %s' % (v1[0] / v1[2], v1[1] / v1[2], np.round(n, 4)))
for W in (0.603, 0.76):
    # plane n.X = -h (table below camera: n points up, so n.X for table points is negative)
    rf, rl = ray(*C[2]), ray(*C[3])
    # X = t*ray, n.X = -h  -> t = -h/(n.ray); choose h so that |X_FR - X_FL| = W
    t = lambda r, h: -h / (n @ r)
    w1 = np.linalg.norm(t(rf, 1) * rf - t(rl, 1) * rl); h = W / w1
    Xc = {k: t(ray(*C[i]), h) * ray(*C[i]) for i, k in enumerate(['BL', 'BR', 'FR', 'FL'])}
    print('\nfront side = %.1f cm: camera height above top h = %.3f m; depth sides %.1f / %.1f cm; Z front %.3f back %.3f'
          % (W * 100, h, 100 * np.linalg.norm(Xc['FL'] - Xc['BL']), 100 * np.linalg.norm(Xc['FR'] - Xc['BR']), Xc['FL'][2], Xc['BL'][2]))
    def onplane(u, v): r = ray(u, v); return t(r, h) * r
    for name, (u, v) in {'f32 landing contact (bottom of toy)': (530, 484), 'f39 contact': (440, 505),
                         'f40 contact': (420, 506), 'f41 contact': (412, 507)}.items():
        X = onplane(u, v); print('  %-36s Z=%.3f range=%.3f' % (name, X[2], np.linalg.norm(X)))
    # toy extents (px) at those Z: centre plane ~ contact Z (level camera)
    for name, (px, u, v) in {'f35 face-on width 83px (Z~f32..f39 mid)': (83, 514, 420),
                             'f39-41 long side 100-110px': (105, 430, 470)}.items():
        Zs = [onplane(530, 484)[2], onplane(440, 505)[2]]
        for Z in Zs: print('  %-36s Z=%.3f -> %.2f cm' % (name, Z, 100 * px * Z / f))
