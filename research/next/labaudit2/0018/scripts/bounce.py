"""Gravity-implied depth from post-bounce parabolas (no dropped frame between v36 and v59), and from the falls."""
import sys, json
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0018/scripts')
from common import *
R = json.load(open(OUT + 'track_refined.json'))
def cap(v): return v + (v >= 12) + (v >= 36)
def fit(name, vs, key='my'):
    c = np.array([cap(v) for v in vs], float); y = np.array([R[name][str(v)][key] for v in vs])
    x = np.array([R[name][str(v)]['mx'] for v in vs])
    p = np.polyfit(c, y, 2); res = y - np.polyval(p, c); a = 2 * p[0]
    return a, 9.8 * F / (a * 625), np.sqrt(np.mean(res ** 2)), -p[1] / (2 * p[0]), x.min(), x.max()
for name, vs in [('tennis', range(37, 49)), ('tennis', range(38, 49)), ('tennis', range(39, 48)),
                 ('soccer', range(40, 49)), ('soccer', range(41, 48)),
                 ('tennis', range(28, 36)), ('tennis', range(30, 36)), ('soccer', range(33, 39)), ('soccer', range(33, 36)),
                 ('box', range(33, 39)), ('pine', range(30, 36)), ('pine', range(31, 36))]:
    a, Z, rms, capex, x0, x1 = fit(name, vs)
    print(f"{name:7s} v{vs[0]}-{vs[-1]}: a={a:5.2f} px/cf2 -> Z={Z:5.2f} m  rms={rms:4.2f}  vertex at c={capex:5.2f}  x {x0:.0f}-{x1:.0f}")
