# Test: can a radial lens distortion term k1 (normalised coords) reconcile the VP gravity with the tracks?
# Joint jar+toy fit, fixed VP gravity, free k1, unanchored (scale from g) and anchored.
import sys; sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0020/scripts')
from common import *
from lm import least_squares
import ballfit as BF
JK = list(range(15, 27)); TK = [15, 16, 17, 19, 20, 21, 22, 23, 24]
def proj_d(P, k1):
    P = np.atleast_2d(P); x = P[:, 0] / P[:, 2]; y = P[:, 1] / P[:, 2]; s = 1 + k1 * (x * x + y * y)
    return np.c_[F * x * s + CX, F * y * s + CY]
for r in 'osx':
    kj, uj = BF.get_uv(r, 'jar', JK); kt, ut = BF.get_uv(r, 'toy', TK)
    tj = tau(np.array(kj)); tt = tau(np.array(kt)); gd = BF.downdir()
    pos = lambda p0, v0, t: p0 + v0 * (np.asarray(t, float) - 0.6)[:, None] + 0.5 * 9.8 * ((np.asarray(t, float) - 0.6)[:, None]) ** 2 * gd
    for anchor in (False, True):
        def res(p):
            rr = np.r_[(proj_d(pos(p[0:3], p[3:6], tj), p[12]) - uj).ravel(), (proj_d(pos(p[6:9], p[9:12], tt), p[12]) - ut).ravel()]
            if anchor: rr = np.r_[rr, 20 * (np.linalg.norm(p[0:3]) - R_JAR - .035) * 100, 20 * (np.linalg.norm(p[6:9]) - R_TOY - .04) * 100]
            return rr
        best = None
        for k0 in (-0.2, 0.0, 0.2):
            s = least_squares(res, np.r_[2.0 * ray(*uj[0]), 0, -2, 1, 2.6 * ray(*ut[0]), -1, 0, -2, k0])
            if best is None or s.cost < best.cost: best = s
        p = best.x; n = 2 * (len(kj) + len(kt)); rms = np.sqrt(np.sum(best.fun[:n] ** 2) / (n / 2))
        Qj = pos(p[0:3], p[3:6], [0.6, 0.64, 0.8]); Qt = pos(p[6:9], p[9:12], [0.6, 0.64, 0.8])
        print(f'{r} anchor={int(anchor)} k1={p[12]:+.3f} rms {rms:.2f} | jar R15 {np.linalg.norm(Qj[0]):.3f} dR16 {100*(np.linalg.norm(Qj[1])-np.linalg.norm(Qj[0])):+.1f}cm | toy R15 {np.linalg.norm(Qt[0]):.3f} dR16 {100*(np.linalg.norm(Qt[1])-np.linalg.norm(Qt[0])):+.1f}cm dR20 {100*(np.linalg.norm(Qt[2])-np.linalg.norm(Qt[0])):+.1f}cm')
