"""Speeds / path length under several depth models (pixel centroids from x, s and o renders)."""
import json, numpy as np
F, CX, CY = 711.0, 640.0, 360.0
B = '/home/user/quantiphy-challenge/research/next/labaudit/0040'
def ray(u, v):
    r = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return r / np.linalg.norm(r)
trs = {R: {int(k): v for k, v in json.load(open(f'{B}/track_{R}.json')).items()} for R in 'xso'}
def rng_lin(t):  # model a: linear between stated anchors
    return 0.7045 + (0.627 - 0.7045) * (t - 1.5) / 0.5
def size_rng(R, i):
    t = trs[R][i]; return F * 0.04 / (t['minor'] * ray(t['u'], t['v'])[2])
for R in 'xs':
    # model b: least-squares line through size ranges f34..f48, then rescaled so the line passes the anchors on average
    I = np.arange(34, 49); r = np.array([size_rng(R, i) for i in I]); p = np.polyfit(I / 24, r, 1)
    k = np.mean([0.7045 / np.polyval(p, 1.5), 0.627 / np.polyval(p, 2.0)])
    models = {'a_lin_anchor': rng_lin, 'b_sizefit': lambda t, p=p: np.polyval(p, t),
              'b_sizefit_scaled': lambda t, p=p, k=k: k * np.polyval(p, t), 'c_const_0.70': lambda t: 0.7045}
    print(f'== render {R}: size-range line {p.round(3)} (at 1.5: {np.polyval(p,1.5):.3f}, at 2.0: {np.polyval(p,2.0):.3f}); anchor rescale {k:.3f}')
    for mn, fn in models.items():
        P = {i: fn(i / 24) * ray(trs[R][i]['u'], trs[R][i]['v']) for i in range(30, 49)}
        v = lambda a, b: np.linalg.norm(P[b] - P[a]) * 24 / (b - a) * 100
        path = sum(np.linalg.norm(P[i + 1] - P[i]) for i in range(36, 46)) * 100     # f36 (1.500) .. f46 (1.917)
        path_b = sum(np.linalg.norm(P[i + 1] - P[i]) for i in range(36, 45)) * 100   # f36 .. f45 (1.875)
        # 1.9 s lies 0.6 frame after f45
        path_19 = path_b + 0.6 * np.linalg.norm(P[46] - P[45]) * 100
        print(f'  {mn:18s} v(1.5)[f36->37]={v(36,37):6.1f} [f35->37 central]={v(35,37):6.1f}  v(1.4)[f33->34]={v(33,34):6.1f} [f34->35]={v(34,35):6.1f} [f33->35]={v(33,35):6.1f}  path f36-45.6={path_19:5.1f}  disp f36-f45.6={np.linalg.norm(0.4*P[45]+0.6*P[46]-P[36])*100:5.1f}')
