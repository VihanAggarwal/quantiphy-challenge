"""Quadratic fits of the falling tracks on the 25 fps capture clock; gravity-implied depth Z = g f / a."""
import sys, json
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0018/scripts')
from common import *
T = json.load(open(OUT + 'track_obj.json'))
def cap(v, drops=(12, 36)):
    return v + sum(v >= d for d in drops)
sel = dict(box=(range(33, 39), 'x'), soccer=(range(33, 39), 'x'), tennis=(range(28, 36), 'x'), pine=(range(30, 36), 'o'))
g = 9.8
res = {}
for name, (vs, src) in sel.items():
    rows = {r['k']: r for r in T[name]}
    for drops in [(12, 36), (12,), (12, 35), (12, 34), (12, 37)]:
        c = np.array([cap(v, drops) for v in vs], float)
        y = np.array([rows[v]['yc' if src == 'x' else 'oyc'] for v in vs])
        x = np.array([rows[v]['xc' if src == 'x' else 'oxc'] for v in vs])
        p = np.polyfit(c, y, 2); resid = y - np.polyval(p, c)
        a = 2 * p[0]  # px / cf^2
        Z = g * F / (a * 625)
        # release time: when vy = 0
        c0 = -p[1] / (2 * p[0])
        print(f"{name:7s} drops={drops} a={a:5.2f} px/cf2  Zgrav={Z:5.2f}  vy=0 at c={c0:5.2f}  rms={np.sqrt(np.mean(resid**2)):5.2f}  resid={np.round(resid,1)}")
    print()
