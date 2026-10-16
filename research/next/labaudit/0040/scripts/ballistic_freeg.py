"""Ballistic fit with free gravity magnitude, depth pinned by the ball's apparent size (D=4 cm) and/or stated ranges."""
import json, numpy as np, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit/0040/scripts')
from ballistic import least_squares, proj, nup, tr, F, CX, CY, Dball
def fit(frames, t0, wsize=1.0, anchors=(), wa=200.0):
    def pos(p, t):
        return p[:3] + p[3:6] * t + 0.5 * (-p[6] * nup) * t * t
    def res(p):
        r = []
        for i in frames:
            t = i / 24 - t0; X = pos(p, t)
            r += list(proj(X) - [tr[i]['u'], tr[i]['v']])
            d = np.linalg.norm(X); cos = X[2] / d
            if wsize: r.append(wsize * (tr[i]['minor'] - F * Dball / (d * cos)))
        for ta, ra in anchors:
            r.append(wa * (np.linalg.norm(pos(p, ta - t0)) - ra))
        return np.array(r)
    i0 = frames[0]; u, v = tr[i0]['u'], tr[i0]['v']
    p0 = np.r_[0.7 * np.array([(u - CX) / F, (v - CY) / F, 1.0]), 0.8, 0, 0, 9.8]
    s = least_squares(res, p0)
    p = s.x
    rr = s.fun[:3 * len(frames)] if wsize else s.fun[:2 * len(frames)]
    out = dict(g=p[6])
    for tq in (1.4, 1.5, 1.54, 1.75, 1.9, 2.0):
        X = pos(p, tq - t0); V = p[3:6] - p[6] * nup * (tq - t0)
        out[tq] = (np.linalg.norm(X), np.linalg.norm(V) * 100)
    return p, out, pos
if __name__ == '__main__':
    for name, frames, t0 in [('A f34-40', list(range(34, 41)), 1.5), ('A f37-40', [37, 38, 39, 40], 1.5),
                             ('B f42-48', list(range(42, 49)), 1.9), ('B f42-47', list(range(42, 48)), 1.9),
                             ('throw f25-32', list(range(25, 33)), 1.3)]:
        for ws, anc in [(1.0, ()), (0.0, ((1.5, 0.7045), (2.0, 0.627))), (1.0, ((1.5, 0.7045), (2.0, 0.627)))]:
            anc2 = tuple(a for a in anc if (frames[0] - 1) / 24 <= a[0] <= (frames[-1] + 1) / 24)
            if ws == 0 and not anc2: continue
            p, o, _ = fit(frames, t0, ws, anc2)
            print(f'{name:12s} size_w={ws} anchors={anc2}: g={o["g"]:.2f}  ' + '  '.join(f't{k}: r={v[0]:.3f} v={v[1]:.0f}' for k, v in o.items() if k != 'g'))
