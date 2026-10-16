"""Ballistic 3D fit of green and white balls in camera b (0054bx tracks); scale from g; gravity from wall-seam VP
(pitch ~30 deg down, roll ~-6.5 deg) or fitted jointly for both balls."""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lm import least_squares
from ballistic_a import tc
F, CX, CY = 711.0, 640.0, 360.0
green = {22: (235.0, 328.3), 23: (278.5, 296.8), 24: (325.0, 272.2), 25: (370.1, 251.1), 26: (413.1, 241.5), 27: (454.4, 239.3),
         28: (488.0, 242.3), 29: (523.3, 252.0), 30: (556.2, 269.6), 31: (584.0, 290.0), 32: (608.0, 314.4), 33: (629.6, 342.3),
         34: (647.5, 371.3), 35: (663.4, 402.1), 36: (689.2, 470.5), 37: (695.7, 490.6)}
white = {20: (221.8, 439.6), 21: (258.9, 382.3), 22: (298.9, 328.6), 23: (338.7, 285.1), 25: (413.2, 223.9), 26: (448.7, 208.4),
         27: (482.4, 198.4), 28: (514.6, 197.9), 29: (541.0, 203.8), 30: (567.4, 218.0), 31: (589.1, 235.2), 32: (608.1, 258.4),
         33: (625.1, 284.8), 34: (639.8, 314.5), 35: (651.6, 344.7), 36: (669.2, 408.5), 37: (677.0, 442.5)}
def gdir(pitch, roll):
    p, r = np.radians(pitch), np.radians(roll)
    return np.array([np.sin(r) * np.cos(p), np.cos(r) * np.cos(p), np.sin(p)])
def proj(P):
    return np.stack([F * P[:, 0] / P[:, 2] + CX, F * P[:, 1] / P[:, 2] + CY], 1)
def fit_joint(tracks, frames_list, pitch=None, roll=None, g=9.8, t0=1.0):
    free = pitch is None
    def unpack(x):
        if free:
            gd = gdir(x[0], x[1]); x = x[2:]
        else:
            gd = gdir(pitch, roll)
        return gd, [x[6 * k:6 * k + 6] for k in range(len(tracks))]
    def res(x):
        gd, pars = unpack(x); out = []
        for tr, frs, p in zip(tracks, frames_list, pars):
            ts = np.array([tc(n) - t0 for n in frs]); uv = np.array([tr[n] for n in frs])
            P = p[:3][None] + p[3:][None] * ts[:, None] + 0.5 * g * gd[None] * ts[:, None] ** 2
            out.append((proj(P) - uv).ravel())
        return np.concatenate(out)
    best = None
    for z0 in (0.8, 1.2, 1.8, 2.5):
        x0 = [30.0, -6.5] if free else []
        for tr, frs in zip(tracks, frames_list):
            u, v = tr[24] if 24 in tr else tr[frs[0]]
            x0 += [(u - CX) / F * z0, (v - CY) / F * z0, z0, 0, 0, 0]
        s = least_squares(res, np.array(x0, float), iters=400)
        if best is None or s.cost < best.cost: best = s
    gd, pars = unpack(best.x)
    out = dict(rms=np.sqrt(np.mean(best.fun ** 2)), gd=gd, balls=[])
    for p in pars:
        X0, V0 = p[:3], p[3:]
        out['balls'].append(dict(pos=lambda t, X0=X0, V0=V0: X0 + V0 * (t - t0) + 0.5 * g * gd * (t - t0) ** 2,
                                 vel=lambda t, V0=V0: V0 + g * gd * (t - t0)))
    if free: out['pitch_roll'] = best.x[:2]
    return out
if __name__ == '__main__':
    G = list(range(25, 36)); W = [21, 22, 23] + list(range(25, 36))
    for label, kw in (('VP walls', dict(pitch=29.9, roll=-6.5)), ('VP walls+door', dict(pitch=31.2, roll=-7.4)), ('pitch 26', dict(pitch=26.0, roll=-5.0)),
                      ('free g dir', dict())):
        for gfr, wfr in ((G, W), (G + [36], W + [36])):
            o = fit_joint([green, white], [gfr, wfr], **kw)
            s = ' '.join('%s: r1.0 %.3f v1.0 %.2f v1.5 %.2f v1.52 %.2f' % (nm, np.linalg.norm(b['pos'](1.0)), np.linalg.norm(b['vel'](1.0)),
                                                                     np.linalg.norm(b['vel'](1.5)), np.linalg.norm(b['vel'](1.52)))
                         for nm, b in zip(('G', 'W'), o['balls']))
            extra = ' pitch/roll %.1f %.1f' % tuple(o['pitch_roll']) if 'pitch_roll' in o else ''
            print('%-14s last %d rms %.2f |%s | %s' % (label, gfr[-1], o['rms'], extra, s))
    print('stated b ranges at 1.0 s: green 1.331, white 1.235')
