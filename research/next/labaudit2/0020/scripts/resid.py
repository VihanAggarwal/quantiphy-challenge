# Residual patterns of the fixed-gravity fits; variants: free g magnitude, joint jar+toy fit with shared free gravity dir.
import sys; sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0020/scripts')
from common import *
from lm import least_squares
import ballfit as BF
T2 = json.load(open(D + 'track2.json'))
JK = list(range(15, 27)); TK = [15, 16, 17, 19, 20, 21, 22, 23, 24]

for r in 'ox':
    for obj, ks, rng, off in (('jar', JK, R_JAR, .035), ('toy', TK, R_TOY, .04)):
        for gfree in (False, True):
            fr = BF.fit(r, obj, ks, rng=rng, off=off, gfree=gfree)
            P = fr['pos'](tau(np.array(fr['ks'])))
            res = project(P) - fr['uv']
            print(r, obj, 'gfree' if gfree else 'fixed', 'rms %.2f' % fr['rms'], ' '.join('%d:(%+.1f,%+.1f)' % (k, a, b) for k, (a, b) in zip(fr['ks'], res)))

# free g magnitude, direction fixed to the VP, anchored
def fit_gmag(r, obj, ks, rng, off, f=F):
    ks2, uv = BF.get_uv(r, obj, ks)
    t = tau(np.array(ks2)); gd = BF.downdir()
    def pos(p, tt):
        dt = (np.asarray(tt, float) - 0.6)[:, None]; return p[:3] + p[3:6] * dt + 0.5 * p[6] * dt ** 2 * gd
    def res(p):
        return np.r_[(project(pos(p, t), f) - uv).ravel(), 20 * (np.linalg.norm(p[:3]) - rng - off) * 100]
    best = None
    for z in (1.5, 2, 2.5, 3):
        p0 = np.r_[z * ray(*uv[0]), 0, -2, 0, 9.8]
        s = least_squares(res, p0)
        if best is None or s.cost < best.cost: best = s
    p = best.x; P = pos(p, t)
    rms = np.sqrt(np.mean(np.sum((project(P, f) - uv) ** 2, 1)))
    return p, rms, pos
print()
for r in 'osx':
    for obj, ks, rng, off in (('jar', JK, R_JAR, .035), ('toy', TK, R_TOY, .04)):
        p, rms, pos = fit_gmag(r, obj, ks, rng, off)
        Q = pos(p, [0.6, 0.64, 0.8]); R = np.linalg.norm(Q, axis=1)
        print(r, obj, 'free |g| (VP dir), anchored: g=%.2f rms %.2f R15/16/20 %.3f/%.3f/%.3f v_fd %.0f disp %.1f' % (p[6], rms, *R, np.linalg.norm(Q[1] - Q[0]) * 2500, np.linalg.norm(Q[2] - Q[0]) * 100))

# joint fit, shared free gravity direction, both anchored
def joint(r, f=F, anchor=True):
    kj, uj = BF.get_uv(r, 'jar', JK); kt, ut = BF.get_uv(r, 'toy', TK)
    tj = tau(np.array(kj)); tt = tau(np.array(kt))
    def gdir(p): q = np.array([p[12], p[13], 1.0]); return q / np.linalg.norm(q)
    def pos(p0, v0, g, t):
        dt = (np.asarray(t, float) - 0.6)[:, None]; return p0 + v0 * dt + 0.5 * 9.8 * dt ** 2 * g
    def res(p):
        g = gdir(p)
        a = (project(pos(p[0:3], p[3:6], g, tj), f) - uj).ravel()
        b = (project(pos(p[6:9], p[9:12], g, tt), f) - ut).ravel()
        rr = np.r_[a, b]
        if anchor: rr = np.r_[rr, 20 * (np.linalg.norm(p[0:3]) - R_JAR - .035) * 100, 20 * (np.linalg.norm(p[6:9]) - R_TOY - .04) * 100]
        return rr
    gd0 = BF.downdir()
    best = None
    for gz in (0.1, 0.3, 0.5):
        p0 = np.r_[2.0 * ray(*uj[0]), 0, -2, 1, 2.6 * ray(*ut[0]), -1, 0, -2, gd0[0] / gz, gd0[1] / gz]
        s = least_squares(res, p0)
        if best is None or s.cost < best.cost: best = s
    p = best.x; g = gdir(p)
    rms = np.sqrt(np.mean(best.fun[:-2] ** 2) * 2) if anchor else np.sqrt(np.mean(best.fun ** 2) * 2)
    Qj = pos(p[0:3], p[3:6], g, [0.6, 0.64, 0.8]); Qt = pos(p[6:9], p[9:12], g, [0.6, 0.64, 0.8])
    return g, rms, Qj, Qt
print()
for r in 'osx':
    for anchor in (True, False):
        g, rms, Qj, Qt = joint(r, anchor=anchor)
        vp = (CX + F * g[0] / g[2], CY + F * g[1] / g[2])
        print(r, 'joint shared-free-g anchor=%d gd %s VP (%.0f,%.0f) rms %.2f | jar R %.3f/%.3f/%.3f v %.0f disp %.1f | toy R %.3f/%.3f/%.3f v %.0f disp %.1f' % (
            anchor, np.round(g, 3), *vp, rms, *np.linalg.norm(Qj, axis=1), np.linalg.norm(Qj[1] - Qj[0]) * 2500, np.linalg.norm(Qj[2] - Qj[0]) * 100,
            *np.linalg.norm(Qt, axis=1), np.linalg.norm(Qt[1] - Qt[0]) * 2500, np.linalg.norm(Qt[2] - Qt[0]) * 100))
