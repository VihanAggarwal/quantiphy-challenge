"""Mixture MC: expected MRA of candidate constants for the two shared labels, over route scenarios (weights) and
ToF noise sigma_z in {0,1,2,3} cm (click jitter 2 px). Uses mc.labels."""
import sys, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0037/scripts')
from mc import labels, mra
c24, c25 = (639.5, 351.5), (626.3, 357.7)
S10 = [(0.10, 0.0060), (0.30, 0.0152), (0.20, 0.0200), (0.20, 0.0227), (0.20, 0.0254)]   # (weight, -dR per frame)
c34 = (498.9, 376.9)
S14 = [(0.40, (483.5, 401.5), 0.906, 0.0152), (0.35, (483.5, 401.5), 0.900, 0.0090),   # whole-ball click: size / joint fit
       (0.25, (485.8, 394.2), 0.906, 0.0152)]                                             # tracked (occluded) click
grid = np.arange(40, 140, 1.0)
for name, scen, cands in (('t=1.0', S10, [48.5, 58.1, 59.0, 65, 70, 72, 75, 80]), ('t=1.4', S14, [55.1, 75.9, 76.6, 85, 90, 95, 100])):
    print('=====', name)
    for sz in (0.0, 0.01, 0.02, 0.03):
        tot = np.zeros(len(cands)); g = np.zeros(len(grid))
        for sc in scen:
            if name == 't=1.0':
                w, dr = sc; L = labels(c24, 1.055, c25, 1.055 - dr, 2.0, sz)
            else:
                w, c1, R0, dr = sc; L = labels(c34, R0, c1, R0 - dr, 2.0, sz)
            tot += w * np.array([mra(a, L).mean() for a in cands]); g += w * np.array([mra(a, L).mean() for a in grid])
        print(f' sz {sz:.2f}: ' + ' '.join(f'{a}:{s:.3f}' for a, s in zip(cands, tot)) + f' | best {grid[g.argmax()]:.0f} ({g.max():.3f})')
