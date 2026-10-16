"""Ballistic 3D fit of the green and white balls in camera a (0054ax tracks), metric scale from g = 9.8 m/s^2.
Video is 24 fps made from a 25 fps capture with one frame dropped every 24 (jumps at n 11->12 and 35->36),
so capture time tc(n) = n/25 (n<=11), (n+1)/25 (12..35), (n+2)/25 (>=36)."""
import numpy as np, sys
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from lm import least_squares
F, CX, CY = 711.0, 640.0, 360.0
def tc(n):
    return (n + (1 if n >= 12 else 0) + (1 if n >= 36 else 0)) / 25.0
green = {24: (600.0, 291.8), 25: (586.5, 284.3), 26: (573.8, 281.9), 27: (559.4, 283.8), 28: (544.7, 290.0), 29: (527.9, 300.4),
         30: (513.1, 314.7), 31: (495.7, 336.0), 32: (477.9, 364.1), 33: (457.2, 397.2), 34: (436.9, 437.0), 35: (414.3, 485.3),
         36: (363.7, 615.8)}
white = {29: (518.8, 265.5), 30: (507.4, 276.7), 31: (494.8, 292.7), 32: (479.6, 315.7), 33: (467.2, 343.3), 34: (449.2, 380.9),
         35: (433.3, 425.7), 36: (391.8, 551.6), 37: (375.7, 613.7)}
def fit(track, frames, pitch_deg, roll_deg=0.0, t0=1.0, g=9.8):
    p, r = np.radians(pitch_deg), np.radians(roll_deg)
    gd = np.array([np.sin(r) * np.cos(p), np.cos(r) * np.cos(p), np.sin(p)])
    gd /= np.linalg.norm(gd)
    ts = np.array([tc(n) - t0 for n in frames]); uv = np.array([track[n] for n in frames])
    def model(x):
        X0, V0 = x[:3], x[3:]
        P = X0[None] + V0[None] * ts[:, None] + 0.5 * g * gd[None] * ts[:, None] ** 2
        return P
    def res(x):
        P = model(x)
        return np.concatenate([F * P[:, 0] / P[:, 2] + CX - uv[:, 0], F * P[:, 1] / P[:, 2] + CY - uv[:, 1]])
    best = None
    for z0 in (1.5, 2.5, 3.5, 5.0):
        u, v = uv[0]
        x0 = np.array([(u - CX) / F * z0, (v - CY) / F * z0, z0, 0, 0, 0])
        s = least_squares(res, x0)
        if best is None or s.cost < best.cost: best = s
    x = best.x
    X0, V0 = x[:3], x[3:]
    vel = lambda t: V0 + g * gd * (t - t0)
    pos = lambda t: X0 + V0 * (t - t0) + 0.5 * g * gd * (t - t0) ** 2
    return dict(rms=np.sqrt(np.mean(best.fun ** 2)), X0=X0, V0=V0, vel=vel, pos=pos, gd=gd)
if __name__ == '__main__':
    for name, tr, frs, t_anchor, r_anchor in (('green', green, list(range(24, 36)), 1.0, 3.039), ('white', white, list(range(29, 36)), 1.0, 3.0735)):
        for pitch in (0.0, 1.0, 2.5, 4.0):
            for use36 in (False, True):
                fr = frs + ([36] if use36 else [])
                if name == 'white' and use36: fr = fr + [37]
                o = fit(tr, fr, pitch)
                rng = np.linalg.norm(o['pos'](t_anchor))
                sp = {t: np.linalg.norm(o['vel'](t)) for t in (1.0, 1.04, 1.48, 1.5, 1.52, 1.54)}
                print('%-5s pitch %.1f frames %d-%d rms %.2f px | range@1.0 %.3f (stated %.3f) | speed ' % (name, pitch, fr[0], fr[-1], o['rms'], rng, r_anchor)
                      + ' '.join('%.2f:%.2f' % kv for kv in sp.items()))
