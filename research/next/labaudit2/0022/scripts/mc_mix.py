"""Expected MRA of constant answers for v(0.8) and v(1.2) over a mixture of label-noise scenarios:
tracks o/s/x, video mapping with/without the drop after video 11, next-frame centre A2/A3, click jitter 2/3 px,
ToF sigma 1/1.5/2/3 cm (weights .2/.3/.3/.2), base-frame reading known (stated) with weight w_known else both noisy."""
import sys, json, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0022/scripts')
from common import *
from plane_traj import traj
T = json.load(open(f'{B}/track.json'))
THR = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95])
grid = np.arange(36, 66, 0.5)
def mra_curve(L):
    rel = np.abs(grid[:, None] - L[None]) / L[None]
    return np.stack([(rel < 1 - t).mean(1) for t in THR], 1).mean(1)
rng = np.random.default_rng(2); N = 20000
def clickP(uv, R, spx, sz, n):
    u = uv[0] + rng.normal(0, spx, n); v = uv[1] + rng.normal(0, spx, n)
    r = np.stack([(u - CX) / F, (v - CY) / F, np.ones(n)], 1); r /= np.linalg.norm(r, axis=1, keepdims=True)
    return r * (R + rng.normal(0, sz, n))[:, None]
SZ = {0.01: .2, 0.015: .3, 0.02: .3, 0.03: .2}
for name, c0, R0, cur in [('v0.8', 20, 1.687, [50.912, 52.202]), ('v1.2', 30, 1.526, [57.255, 55.0, 58.355])]:
    curves = {True: [], False: []}; wts = {True: [], False: []}
    for tag in 'osx':
        C = traj(tag); surf = np.linalg.norm(C, axis=1) - 0.02
        for drop12 in (True, False):
            cc = cap_of_video(np.arange(49), drop12); k0 = int(np.where(cc == c0)[0][0]); k1 = int(np.where(cc == c0 + 1)[0][0])
            k15 = int(np.where(cc == 15)[0][0]); k20 = int(np.where(cc == 20)[0][0])
            scale = np.mean([1.751 / surf[k15], 1.687 / surf[k20]])
            uv0 = np.array(T[tag][k0][:2]); uv1 = np.array(T[tag][k1][:2])
            for R1 in (R0 + (surf[k1] - surf[k0]) * scale, surf[k1] * scale):
                for spx in (2.0, 3.0):
                    for sz, w in SZ.items():
                        for known in (True, False):
                            P0 = clickP(uv0, R0, spx, 0.0 if known else sz, N); P1 = clickP(uv1, R1, spx, sz, N)
                            L = np.linalg.norm(P1 - P0, axis=1) * 2500
                            curves[known].append(mra_curve(L)); wts[known].append(w)
    for wk in (1.0, 0.75, 0.5, 0.0):
        cur_ = wk * np.average(curves[True], axis=0, weights=wts[True]) + (1 - wk) * np.average(curves[False], axis=0, weights=wts[False])
        i = int(cur_.argmax())
        def at(x): return float(np.interp(x, grid, cur_))
        print(f'{name} w_known {wk:.2f}: best {grid[i]:.1f} ({cur_[i]:.3f}); 42 {at(42):.3f} 45 {at(45):.3f} 48 {at(48):.3f} 50 {at(50):.3f} 52 {at(52):.3f}; '
              + ' '.join(f'cur {c}: {at(c):.3f}' for c in cur))
