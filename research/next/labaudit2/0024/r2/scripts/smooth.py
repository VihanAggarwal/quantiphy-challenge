import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from geom import *
from motion import TRK, cap, uv, HB
print('physical (smooth) speeds, slope-plane top surface, quadratic 3D fit vs capture frame')
for tag in 'osx':
    for lo, hi in [(20, 28), (21, 28), (22, 28), (20, 29), (22, 29), (23, 28)]:
        ks = list(range(lo, hi + 1)); c = np.array([cap(k) for k in ks], float)
        X = np.array([on_slope(*uv(tag, k), HB) for k in ks])
        A = np.vstack([c ** 2, c, np.ones_like(c)]).T
        p, *_ = np.linalg.lstsq(A, X, rcond=None)
        f = lambda cc: np.array([cc ** 2, cc, 1.]) @ p
        vel = lambda cc: np.array([2 * cc, 1., 0.]) @ p
        res = X - A @ p
        acc = np.linalg.norm(2 * p[0]) * 625
        print('%s win v%d-%d rms %.2f cm  v(cap25) %.1f  fwd(25->26) %.1f  v(cap30) %.1f  fwd(30->31) %.1f  |a| %.2f m/s2' % (
            tag, lo, hi, np.sqrt((res ** 2).sum(1).mean()) * 100, np.linalg.norm(vel(25)) * 2500, np.linalg.norm(f(26) - f(25)) * 2500,
            np.linalg.norm(vel(30)) * 2500, np.linalg.norm(f(31) - f(30)) * 2500, acc))
