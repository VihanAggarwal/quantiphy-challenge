"""Sensitivity of the plane-route speed at capture 25.5 (forward difference 25->26) to the fit window and model."""
import numpy as np, json
OUT = '/home/user/quantiphy-challenge/research/next/labaudit2/0039'
F, CX, CY = 711.0, 640.0, 360.0
pl = json.load(open(f'{OUT}/plane.json')); n = np.array(pl['n_vp']); H = pl['h_vp']
T = json.load(open(f'{OUT}/track2.json')); R = 0.02
def ray(u, v): r = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return r / np.linalg.norm(r)
def cap(k): return k if k <= 11 else (k + 1 if k <= 35 else k + 2)
for rend in ['0039', '0039s']:
    tr = {int(k): v for k, v in T[rend].items()}
    for a, b in [(21, 40), (22, 40), (23, 40), (24, 40), (22, 36), (23, 33), (21, 30)]:
        ks = list(range(a, b + 1)); cs = np.array([cap(k) for k in ks], float)
        P = np.array([(H - R) / (n @ ray(*tr[k]['cf'][:2])) * ray(*tr[k]['cf'][:2]) for k in ks])
        res = []
        for deg in (1, 2):
            co = [np.polyfit(cs, P[:, j], deg) for j in range(3)]
            pos = lambda c: np.array([np.polyval(co[j], c) for j in range(3)])
            res.append(np.linalg.norm(pos(26) - pos(25)) * 2500)
        print(f'{rend} video {a}-{b}: linear {res[0]:.1f}  quadratic fwd25->26 {res[1]:.1f} cm/s')
