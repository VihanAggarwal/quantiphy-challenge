import json, numpy as np, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from geom import *
from motion import TRK, cap, uv, HB
R25, R30 = 1.0685, 0.9770   # stated: t=1.0 -> capture 25 (video 24); t=1.2 -> capture 30 (video 29)
def vid(c): return c if c <= 11 else (c - 1 if c <= 36 else c - 2)
def mdl(tag, k, key='c', h=HB):
    u, v = uv(tag, k, key); Xs = on_slope(u, v, h); Xt = on_plane(u, v, h)
    return Xs if slope_coords(Xs)[1] > -0.5 else Xt
def rng_interp(c):  # linear in capture time through the two stated anchors
    return R25 + (R30 - R25) * (c - 25) / 5.
for key in ['c', 'b']:
    print('######## click =', 'teal centroid' if key == 'c' else 'teal bbox centre')
    for tag in ['o', 's', 'x']:
        P = {}
        for k in range(18, 37):
            P[cap(k)] = mdl(tag, k, key)
        print('== %s  model ranges cap25 %.3f cap30 %.3f (stated 1.0685 / 0.977)' % (tag, np.linalg.norm(P[25]), np.linalg.norm(P[30])))
        line = 'model fwd speeds (cm/s) cap c->c+1: '
        for c in range(20, 36):
            if c + 1 in P: line += '%d:%.0f ' % (c, np.linalg.norm(P[c + 1] - P[c]) * 2500)
        print(line)
        for c0 in [25, 30]:
            r = {}
            ray0 = ray(*uv(tag, vid(c0), key)); ray1 = ray(*uv(tag, vid(c0 + 1), key))
            m0, m1 = np.linalg.norm(P[c0]), np.linalg.norm(P[c0 + 1])
            Rs = R25 if c0 == 25 else R30
            r['model'] = np.linalg.norm(P[c0 + 1] - P[c0])
            r['stated+interp'] = np.linalg.norm(rng_interp(c0 + 1) * ray1 - Rs * ray0)
            r['stated+model_offset'] = np.linalg.norm((m1 + Rs - m0) * ray1 - Rs * ray0)
            r['stated+model_scale'] = np.linalg.norm((m1 * Rs / m0) * ray1 - Rs * ray0)
            print('  t=%.1f v_label(fwd cap %d->%d):' % (c0 / 25, c0, c0 + 1), '  '.join('%s %.1f' % (k_, v_ * 2500) for k_, v_ in r.items()))
