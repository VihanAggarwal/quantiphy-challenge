"""Ball 3D track per video frame (o and s renders) by the plane route and the size route; compare with the stated ranges."""
import numpy as np, json
OUT = '/home/user/quantiphy-challenge/research/next/labaudit2/0039'
F, CX, CY = 711.0, 640.0, 360.0
pl = json.load(open(f'{OUT}/plane.json')); n = np.array(pl['n_vp']); H = pl['h_vp']
T = json.load(open(f'{OUT}/track2.json'))
R = 0.02
def ray(u, v): r = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return r / np.linalg.norm(r)
def cap(k): return k if k <= 11 else (k + 1 if k <= 35 else k + 2)
for rend in ['0039', '0039s']:
    tr = {int(k): v for k, v in T[rend].items()}
    print('=== render', rend, 'H', round(H, 4))
    for i in range(19, 41):
        u, v, rad = tr[i]['cf']
        rr = ray(u, v)
        rows = []
        for h in (H * 0.98, H, H * 1.02):
            C = (h - R) / (n @ rr) * rr
            rows.append(np.linalg.norm(C))
        # sensitivity to +1 px vertical
        C1 = (H - R) / (n @ ray(u, v + 1)) * ray(u, v + 1)
        print(f'f{i:2d} cap{cap(i):2d} px ({u:6.1f},{v:6.1f}) w {tr[i]["w"]:2d} centre range plane {rows[1]:.4f} (h+-2%: {rows[0]:.4f}-{rows[2]:.4f}); surface {rows[1]-R:.4f}; d/dv {(np.linalg.norm(C1)-rows[1])*100:.2f} cm/px')
