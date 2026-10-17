"""Label-style (noise-free) and physical values for the 0022 motion rows.
Label construction: click the ball centre at capture frames n (25 fps), read the surface range there, back-project,
forward differences on the 25 fps clock. Stated ranges: c15 1.751, c20 1.687, c30 1.526.
Depth routes for frames without a stated range:
  A1 = linear interpolation / extrapolation of the stated ranges (slope after c20: -1.61 cm/frame)
  A2 = nearest stated range + the plane model's change in surface range
  A3 = absolute plane surface range, plane scaled to match the stated c15/c20 ranges (x1.013)
  A4 = absolute plane surface range, unscaled (PnP 76.0 x 60.3)
Physical = plane model (scaled / unscaled) with local quadratic smoothing."""
import sys, json, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0022/scripts')
from common import *
from plane_traj import traj
T = json.load(open(f'{B}/track.json'))
ST = {15: 1.751, 20: 1.687, 30: 1.526}
def vid_of_cap(c, drop12=True):
    ks = np.arange(49); cc = cap_of_video(ks, drop12)
    hit = np.where(cc == c)[0]
    return int(hit[0]) if len(hit) else None
res = {}
for drop12 in (True, False):
    for tag in ['o', 's', 'x']:
        C = traj(tag)                                   # plane centres per video frame (unscaled)
        surf = np.linalg.norm(C, axis=1) - 0.02         # plane surface range per video frame
        k15, k20 = vid_of_cap(15, drop12), vid_of_cap(20, drop12)
        scale = np.mean([ST[15] / surf[k15], ST[20] / surf[k20]])
        def rng(c, route):
            k = vid_of_cap(c, drop12)
            if c in ST: return ST[c]
            if route == 'A1':
                if c < 20: return ST[15] + (ST[20] - ST[15]) * (c - 15) / 5
                return ST[20] + (ST[30] - ST[20]) * (c - 20) / 10
            if route == 'A2':
                a = min(ST, key=lambda s: abs(s - c) if s <= c else 99)
                return ST[a] + (surf[k] - surf[vid_of_cap(a, drop12)]) * scale
            if route == 'A3': return surf[k] * scale
            if route == 'A4': return surf[k]
        def P(c, route):
            k = vid_of_cap(c, drop12); return rng(c, route) * ray(*T[tag][k][:2])
        line = []
        for route in ['A1', 'A2', 'A3', 'A4']:
            v08 = np.linalg.norm(P(21, route) - P(20, route)) * 25 * 100
            v12 = np.linalg.norm(P(31, route) - P(30, route)) * 25 * 100
            v12n = np.linalg.norm(P(32, route) - P(31, route)) * 25 * 100
            a12 = (v12n - v12) * 25
            vv = (P(32, route) - 2 * P(31, route) + P(30, route)) * 625 * 100
            d = np.linalg.norm(P(40, route) - P(15, route)) * 100
            res[(drop12, tag, route)] = dict(v08=v08, v12=v12, a12=a12, avec=np.linalg.norm(vv), disp=d)
            line.append(f'{route}: v.8 {v08:5.1f} v1.2 {v12:5.1f} a1.2(speed diff) {a12:7.1f} |a vec| {np.linalg.norm(vv):6.1f} disp {d:5.1f}')
        # physical (plane, scaled / unscaled)
        cc = cap_of_video(np.arange(49), drop12)
        def smooth_v(k, sc, hw=5):
            idx = np.arange(k - hw, k + hw + 1); t = cc[idx] / 25.0 - cc[k] / 25.0
            co = [np.polyfit(t, C[idx, j] * sc, 2) for j in range(3)]
            return np.linalg.norm([q[1] for q in co]) * 100, np.linalg.norm([2 * q[0] for q in co]) * 100
        k30, k40 = vid_of_cap(30, drop12), vid_of_cap(40, drop12)
        for sc, nm in [(scale, 'scaled'), (1.0, 'unscaled')]:
            v8, _ = smooth_v(k20, sc); v12, a12 = smooth_v(k30, sc)
            dph = np.linalg.norm(C[k40] - C[k15]) * sc * 100
            line.append(f'phys {nm}: v.8 {v8:5.1f} v1.2 {v12:5.1f} disp {dph:5.1f}')
        print(f'drop12={drop12} {tag} (scale {scale:.4f}; video k15 {k15} k20 {k20} k30 {k30} k40 {k40})')
        for l in line: print('   ', l)
