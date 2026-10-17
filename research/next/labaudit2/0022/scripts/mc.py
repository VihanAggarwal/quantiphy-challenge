"""Label distribution for v(0.8) and v(1.2) when the base-frame range is the stated one (known) and only the
next-frame ToF reading and both clicks are noisy. Click jitter sigma_px (2 px), ToF sigma_z per reading.
Centre of the next-frame reading: A2 (stated + plane change: ToF offset persists) or A3 (absolute plane range,
scaled to the stated c15/c20: the c30 offset of -2.6 cm is one-off noise). MRA-optimal constant and scores of
the current answers. Also the repo emulator's setting (both readings noisy) for comparison."""
import sys, json, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0022/scripts')
from common import *
from plane_traj import traj
T = json.load(open(f'{B}/track.json'))
THR = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95])
def mra(c, L): return ((np.abs(c - L) / L)[:, None] < 1 - THR).mean(-1).mean()
rng = np.random.default_rng(1); N = 100000
def clickP(uv, R, spx, sz, n):
    u = uv[0] + rng.normal(0, spx, n); v = uv[1] + rng.normal(0, spx, n)
    r = np.stack([(u - CX) / F, (v - CY) / F, np.ones(n)], 1); r /= np.linalg.norm(r, axis=1, keepdims=True)
    return r * (R + (rng.normal(0, sz, n) if sz else np.zeros(n)))[:, None]
tag = 'o'
C = traj(tag); surf = np.linalg.norm(C, axis=1) - 0.02; scale = 1.013
rows = {'v0.8': (19, 20, 1.687, [50.912, 52.202]), 'v1.2': (29, 30, 1.526, [57.255, 55.0, 58.355])}
for name, (k0, k1, R0, cur) in rows.items():
    uv0 = np.array(T[tag][k0][:2]); uv1 = np.array(T[tag][k1][:2])
    cent = {'A2': R0 + (surf[k1] - surf[k0]) * scale, 'A3': surf[k1] * scale}
    for cn, R1 in cent.items():
        for sz in (0.0, 0.01, 0.015, 0.02, 0.03):
            for both in (False, True):
                if both and cn == 'A3': continue
                P0 = clickP(uv0, R0, 2.0, sz if both else 0.0, N); P1 = clickP(uv1, R1, 2.0, sz, N)
                L = np.linalg.norm(P1 - P0, axis=1) * 25 * 100
                grid = np.arange(30, 90, 0.5); sc = np.array([mra(c, L) for c in grid])
                s_cur = ' '.join(f'{c}:{mra(c, L):.3f}' for c in cur)
                print(f'{name} centre {cn} (R1 {R1:.4f}) sz {sz*100:.1f} cm {"both-noisy" if both else "base-known"}: '
                      f'median {np.median(L):.1f}, best const {grid[sc.argmax()]:.1f} ({sc.max():.3f}); '
                      f'42: {mra(42, L):.3f}, 45: {mra(45, L):.3f}, 48: {mra(48, L):.3f}; current {s_cur}')
