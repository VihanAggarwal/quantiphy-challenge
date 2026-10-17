"""3D ballistic fit of the flight between the table bounces (video 34..40 = capture 35..42) on the 25 fps capture
clock (drop between video 35 and 36). Gravity along the table normal (round-1 plane). Variants:
 (G) g = 9.8 fixed, range free (scale from gravity);  (D) range pinned to the stated anchor at c38, g free.
Reports range, speed at capture times 1.40, 1.44, 1.48, 1.50, 1.52, 1.56 and the FD-equivalents."""
import sys, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0040/scripts')
import motion as M
F, CX, CY = M.F, M.CX, M.CY
nup = -np.array([-0.0265, 0.9996, 0.0035]); nup /= np.linalg.norm(nup)   # 'up' in camera coords (y down)
def lsq(fun, x0, iters=300):
    x = np.array(x0, float); lam = 1e-3; f = fun(x); c = f @ f
    for _ in range(iters):
        J = np.empty((len(f), len(x)))
        for k in range(len(x)):
            h = 1e-6 * max(1.0, abs(x[k])); xp = x.copy(); xp[k] += h; J[:, k] = (fun(xp) - f) / h
        A = J.T @ J; g = J.T @ f
        while True:
            dx = -np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-12), g); fn = fun(x + dx); cn = fn @ fn
            if cn < c: x, f, c = x + dx, fn, cn; lam = max(lam / 3, 1e-9); break
            lam *= 4
            if lam > 1e9: break
        if lam > 1e9 or np.abs(dx).max() < 1e-12: break
    return x, f
def proj(X): return np.array([F * X[0] / X[2] + CX, F * X[1] / X[2] + CY])
for R in ('x', 's'):
    for mode in ('caps', 'cent'):
        tr = M.load(R, mode)
        for frames in ((35, 36, 37, 38, 39), (34, 35, 36, 37, 38, 39), (35, 36, 37, 38, 39, 40)):
            t = {n: (M.cap(n) - 38) / 25.0 for n in frames}       # t=0 at capture 38 (video 36)
            def pos(p, tt, g): return p[:3] + p[3:6] * tt - 0.5 * g * nup * tt * tt
            for var in ('G', 'D'):
                def res(p):
                    g = 9.8 if var == 'G' else p[6]
                    r = []
                    for n in frames:
                        r += list(proj(pos(p, t[n], g)) - [tr[n]['u'], tr[n]['v']])
                    if var == 'D':
                        r.append(300 * (np.linalg.norm(pos(p, 0.0, g)) - 0.7245))   # centre range at c38 = stated surface + 2 cm
                    return np.array(r)
                u, v = tr[36]['u'], tr[36]['v']
                p0 = np.r_[0.72 * M.ray(u, v), 0.8, -0.1, -0.1] if var == 'G' else np.r_[0.72 * M.ray(u, v), 0.8, -0.1, -0.1, 9.8]
                p, f = lsq(res, p0)
                g = 9.8 if var == 'G' else p[6]
                rr = f[:2 * len(frames)].reshape(-1, 2); rms = np.sqrt((rr ** 2).mean())
                def V(tc): return p[3:6] - g * nup * tc
                def X(tc): return pos(p, tc, g)
                s = lambda c: np.linalg.norm(V((c - 38) / 25)) * 100
                fd = lambda c0, c1: np.linalg.norm(X((c1 - 38) / 25) - X((c0 - 38) / 25)) * 25 / (c1 - c0) * 100
                print(f'{R} {mode} v{frames[0]}-{frames[-1]} {var}: g={g:5.2f} rms={rms:4.1f}px range@c38={np.linalg.norm(X(0)):.3f} '
                      f'v(c35)={s(35):5.1f} v(c35.5)={s(35.5):5.1f} v(c37.5)={s(37.5):5.1f} v(c38)={s(38):5.1f} v(c38.5)={s(38.5):5.1f} '
                      f'FD38-39={fd(38,39):5.1f} FD35-36={fd(35,36):5.1f} vr={V(0)@X(0)/np.linalg.norm(X(0))*100:+5.1f}')
