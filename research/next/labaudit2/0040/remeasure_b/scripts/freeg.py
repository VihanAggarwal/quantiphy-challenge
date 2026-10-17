import sys; sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0040/remeasure_b/scripts')
import numpy as np
from lm import least_squares
from arcs import load, cap, proj, fit_arc
from plane import plane
tr = load(sys.argv[1] if len(sys.argv) > 1 else 'captured_0040')
def joint(f, arcs, gfree=True, gmag=981.0):
    n, d0 = plane(f); g0 = -n / np.linalg.norm(n)
    # params: per arc X0,V0 (6) + gravity angles (2: tilt about x and z)
    inits = []
    for fr, tref in arcs:
        p, r, P = fit_arc(fr, f, tr, tref, init_rng=72)
        inits.append(p)
    def gdir(a):
        # rotate g0 by small angles a[0] about camera x axis, a[1] about camera z axis
        ax, az = a
        Rx = np.array([[1, 0, 0], [0, np.cos(ax), -np.sin(ax)], [0, np.sin(ax), np.cos(ax)]])
        Rz = np.array([[np.cos(az), -np.sin(az), 0], [np.sin(az), np.cos(az), 0], [0, 0, 1]])
        return Rz @ Rx @ g0
    def res(q):
        out = []
        G = gdir(q[-2:]) * gmag if gfree else g0 * gmag
        for i, (fr, tref) in enumerate(arcs):
            p = q[6 * i:6 * i + 6]
            ts = (np.array([cap(k) for k in fr]) - tref) / 25.
            X = p[None, :3] + p[None, 3:6] * ts[:, None] + 0.5 * G[None] * ts[:, None] ** 2
            out.append((proj(X, f) - np.array([tr[k] for k in fr])).ravel())
        return np.concatenate(out)
    q0 = np.r_[np.concatenate(inits), 0, 0]
    sol = least_squares(res, q0)
    q = sol.x
    r = sol.fun
    G = gdir(q[-2:])
    ang = np.degrees(np.arccos(np.clip(G @ g0, -1, 1)))
    print('f %d joint rms %.2f  gravity tilt from table normal %.2f deg (ax %.2f az %.2f)' % (f, np.sqrt((r ** 2).mean()), ang, *np.degrees(q[-2:])))
    for i, (fr, tref) in enumerate(arcs):
        p = q[6 * i:6 * i + 6]
        print('   arc tref c%d: range %.1f  V %s |V| %.1f' % (tref, np.linalg.norm(p[:3]), p[3:6].round(1), np.linalg.norm(p[3:6])))
    return q
for f in [711]:
    joint(f, [(list(range(34, 41)), 38), (list(range(42, 49)), 50)], gfree=False)
    joint(f, [(list(range(34, 41)), 38), (list(range(42, 49)), 50)], gfree=True)
    joint(f, [(list(range(28, 33)), 30), (list(range(34, 41)), 38), (list(range(42, 49)), 50)], gfree=True)
