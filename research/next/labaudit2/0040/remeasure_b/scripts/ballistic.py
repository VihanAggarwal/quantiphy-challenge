import numpy as np, json, sys
import sys; sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0040/remeasure_b/scripts')
from lm import least_squares

from plane import plane, ray_plane
B = '/home/user/quantiphy-challenge/research/next/labaudit2/0040/remeasure_b/'
def cap(k): return k + (k >= 12) + (k >= 36)
def load(V='captured_0040'):
    T = json.load(open(B + 'track_%s.json' % V))
    return {int(k): np.array([v['cx'], v['cy']]) for k, v in T.items()}
def fit(frames, f, track, gmag=981.0, tref=38, fixg=True, extra_free=False):
    n, d0 = plane(f)
    gdir = -n / np.linalg.norm(n)
    ks = np.array(frames); ts = (np.array([cap(k) for k in ks]) - tref) / 25.0
    obs = np.array([track[k] for k in ks])
    def proj(X):
        return np.stack([f * X[:, 0] / X[:, 2] + 640, f * X[:, 1] / X[:, 2] + 360], 1)
    def pos(p, t):
        X0, V0 = p[:3], p[3:6]
        g = gdir * gmag if fixg else p[6:9]
        return X0[None] + V0[None] * t[:, None] + 0.5 * g[None] * t[:, None] ** 2
    def res(p): return (proj(pos(p, ts)) - obs).ravel()
    # init: point at plane +3cm at tref-frame pixel
    k0 = ks[np.argmin(np.abs(ts))]
    X0 = ray_plane(*track[k0], f, h=8)
    p0 = np.r_[X0, 50, -50, -100]
    if not fixg: p0 = np.r_[p0, gdir * gmag]
    sol = least_squares(res, p0, method='lm')
    r = sol.fun.reshape(-1, 2)
    return sol.x, r, pos, ts, gdir
if __name__ == '__main__':
    V = sys.argv[1] if len(sys.argv) > 1 else 'captured_0040'
    tr = load(V)
    for f in [711, 740]:
        for frames in [list(range(33, 42)), list(range(34, 41)), list(range(34, 42)), list(range(33, 41))]:
            p, r, pos, ts, gdir = fit(frames, f, tr)
            X0, V0 = p[:3], p[3:6]
            # values at capture 37,38,39
            tt = (np.array([37, 38, 39]) - 38) / 25.
            P = pos(p, tt)
            rng = np.linalg.norm(P, axis=1)
            vA = np.linalg.norm(P[2] - P[1]) * 25; vB = np.linalg.norm(P[1] - P[0]) * 25
            vinst = np.linalg.norm(V0)
            n, d0 = plane(f)
            hgt = [abs(d0) - (-n @ X) * np.sign(d0) * -1 for X in pos(p, ts)]
            # height above table: signed distance from plane toward camera
            s = np.sign(d0)
            hgt = [s * (d0 - n @ X) for X in pos(p, ts)]
            print('f %d frames %d-%d rms %.2f px max %.2f | range c37 %.1f c38 %.1f c39 %.1f | |v| c38 %.1f  fwdA(38->39) %.1f fwdB(37->38) %.1f cm/s | V0 %s' % (
                f, frames[0], frames[-1], np.sqrt((r ** 2).mean()), np.abs(r).max(), *rng, vinst, vA, vB, V0.round(1)))
            print('    heights above table (cm) at frames:', dict(zip(frames, np.round(hgt, 1))))
