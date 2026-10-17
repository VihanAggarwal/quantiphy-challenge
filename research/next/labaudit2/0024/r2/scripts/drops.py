import json, numpy as np, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from geom import *
TR_ = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'track.json')))
H = 0.0073
def along(tag, key='c'):
    out = {}
    for r in TR_[tag]:
        if r is None: continue
        u, v = (r['cx'], r['cy']) if key == 'c' else (r['bx'], r['by'])
        out[r['k']] = slope_coords(on_slope(u, v, H))[1]
    return out
for tag in ['o', 's', 'x']:
    for key in ['c', 'b']:
        s = along(tag, key)
        ks = list(range(19, 30))
        y = np.array([s[k] for k in ks])
        print(tag, key, 'along-slope (cm):', ' '.join('%5.1f' % v for v in y))
        print('      steps:', ' '.join('%5.2f' % v for v in -np.diff(y)))
        # fit quadratic in capture time for drop hypotheses (drop between video d-1 and d), window 20..29
        for lo in [20, 21, 22]:
            ks2 = list(range(lo, 30)); y2 = np.array([s[k] for k in ks2])
            res = []
            for d in [None] + list(range(lo + 1, 30)):
                c = np.array([k + (1 if (d is not None and k >= d) else 0) for k in ks2], float)
                A = np.vstack([c ** 2, c, np.ones_like(c)]).T
                p, *_ = np.linalg.lstsq(A, y2, rcond=None); r = y2 - A @ p
                res.append((np.sqrt(np.mean(r ** 2)), d, -2 * p[0] * 625 / 100))
            res.sort(key=lambda t: t[0])
            print('   win %d-29 best drops:' % lo, ' '.join('d=%s rms %.2f a=%.2f' % (d, e, a) for e, d, a in res[:4]))
