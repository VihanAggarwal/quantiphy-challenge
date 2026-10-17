"""Per-capture-step speeds (plane route) and pixel steps; windowed average speeds."""
import numpy as np, json
OUT = '/home/user/quantiphy-challenge/research/next/labaudit2/0039'
F, CX, CY = 711.0, 640.0, 360.0
pl = json.load(open(f'{OUT}/plane.json')); n = np.array(pl['n_vp']); H = pl['h_vp']
T = json.load(open(f'{OUT}/track2.json')); R = 0.02
def ray(u, v): r = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return r / np.linalg.norm(r)
def cap(k): return k if k <= 11 else (k + 1 if k <= 35 else k + 2)
for rend in ['0039', '0039s']:
    tr = {int(k): v for k, v in T[rend].items()}
    P = {k: (H - R) / (n @ ray(*tr[k]['cf'][:2])) * ray(*tr[k]['cf'][:2]) for k in range(19, 42)}
    print('==', rend)
    line = []
    for k in range(19, 41):
        dc = cap(k + 1) - cap(k)
        s = np.linalg.norm(P[k + 1] - P[k]) / dc * 2500
        du = (tr[k + 1]['cf'][0] - tr[k]['cf'][0]) / dc; dv = (tr[k + 1]['cf'][1] - tr[k]['cf'][1]) / dc
        line.append(f'{k}->{k+1}(c{cap(k)}-{cap(k+1)}): {s:5.1f} cm/s du {du:5.2f} dv {dv:5.2f}')
    print('\n'.join(line))
    for a, b in [(20, 24), (21, 27), (22, 28), (24, 30), (24, 36), (28, 34), (30, 36), (34, 40), (36, 40)]:
        print(f'  window video {a}-{b} (cap {cap(a)}-{cap(b)}): {np.linalg.norm(P[b]-P[a])/(cap(b)-cap(a))*2500:.1f} cm/s')
