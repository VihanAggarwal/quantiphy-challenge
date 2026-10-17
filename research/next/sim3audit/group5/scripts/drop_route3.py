# simulation_0201: line-model fit. Unknowns: f, fall direction g (2 dof), v0; P0 = 0.156 along frame-0 ray; s(t)=v0 t + 0.5*9.7 t^2.
# Constraint |P(0.1)| = 0.186. Fit to centroids frames 0-9 (own track). Also report variant with a free and f from range constraint only.
import json, numpy as np
import sys; sys.path.insert(0, "/home/user/quantiphy-challenge/research/next/sim3audit/group5/scripts"); from lm import least_squares as _ls
def least_squares(f, x0, bounds=None):
    return _ls(f, x0, bounds[0], bounds[1])
tr = json.load(open('/home/user/quantiphy-challenge/research/next/sim3audit/group5/drop_track.json'))
u = np.array([t['cx'] for t in tr]); v = np.array([t['cy'] for t in tr]); tt = np.array([t['i'] for t in tr]) / 60.0
c = 1280.0
def model(p, a_fixed=None):
    f, th, ph, v0 = p[:4]
    a = 9.7 if a_fixed is None else p[4]
    g = np.array([np.sin(th) * np.cos(ph), np.cos(th), np.sin(th) * np.sin(ph)])
    d0 = np.array([(u[0] - c) / f, (v[0] - c) / f, 1.0]); d0 /= np.linalg.norm(d0)
    P0 = 0.156 * d0
    s = v0 * tt + 0.5 * a * tt**2
    P = P0[None] + s[:, None] * g[None]
    pu = c + f * P[:, 0] / P[:, 2]; pv = c + f * P[:, 1] / P[:, 2]
    return P, pu, pv
def resid(p, n=10, a_free=False, wr=200.0):
    P, pu, pv = model(p, a_fixed=1 if a_free else None)
    r = np.concatenate([(pu - u)[:n], (pv - v)[:n]])
    r6 = np.linalg.norm(P[6]) - 0.186
    return np.concatenate([r, [wr * 1000 * r6 / 10]])
best = None
for f0 in [2000, 3000, 4000, 5000]:
    for th0 in [0.5, 0.8, 1.0]:
        for ph0 in [1.0, 1.4, 1.7]:
            try:
                s = least_squares(resid, [f0, th0, ph0, 0.0], bounds=([500, 0, -np.pi, -2], [20000, np.pi, np.pi, 2]))
            except Exception as e:
                continue
            if best is None or s.cost < best.cost: best = s
p = best.x
P, pu, pv = model(p)
print('a fixed 9.7: f=%.0f  v0=%.4f  rms px=%.2f  |P6|=%.4f' % (p[0], p[3], np.sqrt(np.mean(np.r_[pu-u, pv-v]**2)), np.linalg.norm(P[6])))
for T in [0.05, 0.1, 0.2]: print('   t=%.2f backward v=%.3f  inst=%.3f' % (T, p[3] + 9.7 * (T - 1/120), p[3] + 9.7*T))
# frames 0-7 only
best2 = None
for f0 in [2000, 3000, 4000, 5000]:
    for th0 in [0.5, 0.8, 1.0]:
        for ph0 in [1.0, 1.4, 1.7]:
            s = least_squares(lambda q: resid(q, n=8), [f0, th0, ph0, 0.0], bounds=([500, 0, -np.pi, -2], [20000, np.pi, np.pi, 2]))
            if best2 is None or s.cost < best2.cost: best2 = s
q = best2.x
print('frames0-7: f=%.0f v0=%.4f' % (q[0], q[3]))
# a free: does the data itself recover ~9.7?
best3 = None
for f0 in [2000, 3000, 4000, 5000]:
    for th0 in [0.5, 0.8, 1.0]:
        for ph0 in [1.0, 1.4, 1.7]:
            for a0 in [5, 10, 15]:
                s = least_squares(lambda q: resid(q, a_free=True), [f0, th0, ph0, 0.0, a0], bounds=([500, 0, -np.pi, -2, 0], [20000, np.pi, np.pi, 2, 50]))
                if best3 is None or s.cost < best3.cost: best3 = s
q = best3.x
print('a free: f=%.0f v0=%.4f a=%.2f cost=%.3f' % (q[0], q[3], q[4], best3.cost))
