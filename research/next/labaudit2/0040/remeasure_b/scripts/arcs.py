import sys; sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0040/remeasure_b/scripts')
import numpy as np, json
from lm import least_squares
from plane import plane, ray_plane
B = '/home/user/quantiphy-challenge/research/next/labaudit2/0040/remeasure_b/'
def cap(k): return k + (k >= 12) + (k >= 36)
def load(V='captured_0040'):
    T = json.load(open(B + 'track_%s.json' % V))
    return {int(k): np.array([v['cx'], v['cy']]) for k, v in T.items()}
def proj(X, f):
    return np.stack([f * X[:, 0] / X[:, 2] + 640, f * X[:, 1] / X[:, 2] + 360], 1)
def fit_arc(frames, f, track, tref, gmag=981.0, gdir=None, init_rng=75.0, w=None):
    n, d0 = plane(f)
    if gdir is None: gdir = -n / np.linalg.norm(n)
    ks = np.array(frames); ts = (np.array([cap(k) for k in ks]) - tref) / 25.0
    obs = np.array([track[k] for k in ks])
    def pos(p, t):
        return p[None, :3] + p[None, 3:6] * t[:, None] + 0.5 * gmag * gdir[None] * t[:, None] ** 2
    def res(p): return (proj(pos(p, ts), f) - obs).ravel()
    best = None
    for r0 in [init_rng * 0.8, init_rng, init_rng * 1.25]:
        # init from pixels: positions at depth r0 -> finite-difference velocity
        rays = np.c_[(obs[:, 0] - 640) / f, (obs[:, 1] - 360) / f, np.ones(len(obs))]
        P = rays / np.linalg.norm(rays, axis=1)[:, None] * r0
        A = np.c_[np.ones(len(ts)), ts]
        coef = np.linalg.lstsq(A, P - 0.5 * gmag * gdir[None] * ts[:, None] ** 2, rcond=None)[0]
        p0 = np.r_[coef[0], coef[1]]
        sol = least_squares(res, p0)
        c = (sol.fun ** 2).sum()
        if best is None or c < best[0]: best = (c, sol)
    sol = best[1]
    return sol.x, sol.fun.reshape(-1, 2), (lambda t, p=sol.x: pos(p, np.atleast_1d(np.array(t, float))))
def height(X, f):
    n, d0 = plane(f); s = np.sign(d0)
    return s * (d0 - X @ n)
if __name__ == '__main__':
    V = sys.argv[1] if len(sys.argv) > 1 else 'captured_0040'
    tr = load(V)
    for f in [711, 740]:
        print('==== f', f)
        for fr in [range(34, 41), range(33, 41), range(34, 40), range(35, 41)]:
            fr = list(fr)
            p, r, P = fit_arc(fr, f, tr, tref=38)
            X = P((np.array([37, 38, 39]) - 38) / 25.)
            rng = np.linalg.norm(X, axis=1)
            vA = np.linalg.norm(X[2] - X[1]) * 25; vB = np.linalg.norm(X[1] - X[0]) * 25
            hs = height(P((np.array([cap(k) for k in fr]) - 38) / 25.), f)
            print('arc2 %d-%d rms %.2f max %.2f | centre range c37 %.1f c38 %.1f c39 %.1f | |v(c38)| %.1f  chord A %.1f B %.1f | V %s | h %s' % (
                fr[0], fr[-1], np.sqrt((r**2).mean()), np.abs(r).max(), *rng, np.linalg.norm(p[3:6]), vA, vB, p[3:6].round(1), hs.round(1)))
        for fr in [range(42, 49), range(43, 49), range(42, 48)]:
            fr = list(fr)
            p, r, P = fit_arc(fr, f, tr, tref=50, init_rng=65)
            X = P(0.0)
            hs = height(P((np.array([cap(k) for k in fr]) - 50) / 25.), f)
            print('arc3 %d-%d rms %.2f max %.2f | centre range c50 %.1f | V %s |v| %.1f | h %s' % (fr[0], fr[-1], np.sqrt((r**2).mean()), np.abs(r).max(), np.linalg.norm(X), p[3:6].round(1), np.linalg.norm(p[3:6]), hs.round(1)))
        for fr in [range(28, 33), range(27, 33)]:
            fr = list(fr)
            p, r, P = fit_arc(fr, f, tr, tref=30, init_rng=90)
            hs = height(P((np.array([cap(k) for k in fr]) - 30) / 25.), f)
            print('arc1 %d-%d rms %.2f | ranges %s | h %s' % (fr[0], fr[-1], np.sqrt((r**2).mean()), np.linalg.norm(P((np.array([cap(k) for k in fr]) - 30) / 25.), axis=1).round(1), hs.round(1)))
