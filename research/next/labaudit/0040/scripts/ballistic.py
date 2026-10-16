"""Fit ballistic 3D segments to the 2D track (gravity 9.8 m/s^2 along -table normal gives the scale).
Independent check: stated ranges at t=1.5 (0.7045) and t=2.0 (0.627); size-based ranges."""
import json, numpy as np, sys

class _R: pass
def least_squares(fun, x0, iters=200):
    x = np.array(x0, float); lam = 1e-3
    f = fun(x); c = f @ f
    for _ in range(iters):
        J = np.empty((len(f), len(x)))
        for k in range(len(x)):
            h = 1e-6 * max(1.0, abs(x[k])); xp = x.copy(); xp[k] += h
            J[:, k] = (fun(xp) - f) / h
        A = J.T @ J; g = J.T @ f
        while True:
            dx = -np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-12), g)
            fn = fun(x + dx); cn = fn @ fn
            if cn < c:
                x, f, c = x + dx, fn, cn; lam = max(lam / 3, 1e-9); break
            lam *= 4
            if lam > 1e9: break
        if lam > 1e9 or np.abs(dx).max() < 1e-10: break
    r = _R(); r.x = x; r.fun = f; return r
F, CX, CY, Dball = 711.0, 640.0, 360.0, 0.04
B = '/home/user/quantiphy-challenge/research/next/labaudit/0040'
R = sys.argv[1] if len(sys.argv) > 1 else 'x'
tr = {int(k): v for k, v in json.load(open(f'{B}/track_{R}.json')).items()}
nup = np.array([0.026, -1.0, -0.004]); nup /= np.linalg.norm(nup)
G = -9.8 * nup
def proj(X):
    return np.array([F * X[0] / X[2] + CX, F * X[1] / X[2] + CY])
def pos(p, t):
    return p[:3] + p[3:] * t + 0.5 * G * t * t
def fit(frames, t0, wsize=0.0, fps=24.0):
    ts = {i: i / fps - t0 for i in frames}
    def res(p):
        r = []
        for i in frames:
            X = pos(p, ts[i]); r += list(proj(X) - [tr[i]['u'], tr[i]['v']])
            if wsize > 0:
                d = np.linalg.norm(X); cos = X[2] / d
                r.append(wsize * (tr[i]['minor'] - F * Dball / (d * cos)))
        return np.array(r)
    i0 = frames[0]
    u, v = tr[i0]['u'], tr[i0]['v']
    p0 = np.r_[0.7 * np.array([(u - CX) / F, (v - CY) / F, 1.0]), 0.8, 0, 0]
    s = least_squares(res, p0)
    return s, ts
def report(name, frames, t0, wsize=0.0, fps=24.0):
    s, ts = fit(frames, t0, wsize, fps)
    p = s.x
    rr = s.fun[: 2 * len(frames)].reshape(-1, 2)
    print(f'== {name} frames {frames[0]}-{frames[-1]} wsize={wsize} fps={fps}: rms reproj {np.sqrt((rr**2).mean()):.2f}px')
    for tq in (1.4, 1.5, 1.54, 1.75, 1.9, 2.0):
        X = pos(p, tq - t0); V = p[3:] + G * (tq - t0)
        print(f'   t={tq}: range {np.linalg.norm(X):.3f}  speed {np.linalg.norm(V)*100:6.1f} cm/s  P={np.round(X*100,1)}')
    return p
if __name__ == '__main__':
    for w in (0.0, 0.3):
        report('seg A (after table bounce f33)', list(range(34, 41)), 1.5, w)
        report('seg A minus f36', [34, 35, 37, 38, 39, 40], 1.5, w)
        report('seg A2 f37-f40', [37, 38, 39, 40], 1.5, w)
        report('seg B (after bounce f41)', list(range(42, 49)), 1.9, w)
        report('seg B f42-47', list(range(42, 48)), 1.9, w)
        report('seg 0 throw f25-f32', list(range(25, 33)), 1.3, w)
