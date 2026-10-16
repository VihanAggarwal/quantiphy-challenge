"""Tiny Levenberg-Marquardt (numpy only; scipy is not installed)."""
import numpy as np
class R:  # result
    pass
def least_squares(fun, x0, iters=200, eps=1e-6):
    x = np.asarray(x0, float).copy(); lam = 1e-3
    r = fun(x); cost = 0.5 * r @ r
    for _ in range(iters):
        J = np.empty((r.size, x.size))
        for k in range(x.size):
            h = eps * max(1.0, abs(x[k])); xp = x.copy(); xp[k] += h
            J[:, k] = (fun(xp) - r) / h
        A = J.T @ J; g = J.T @ r
        improved = False
        for _ in range(20):
            try:
                dx = -np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-12), g)
            except np.linalg.LinAlgError:
                lam *= 10; continue
            xn = x + dx; rn = fun(xn); cn = 0.5 * rn @ rn
            if np.isfinite(cn) and cn < cost:
                x, r, cost = xn, rn, cn; lam = max(lam / 3, 1e-9); improved = True; break
            lam *= 10
        if not improved or np.linalg.norm(dx) < 1e-10 * (1 + np.linalg.norm(x)):
            break
    o = R(); o.x = x; o.fun = r; o.cost = cost
    return o
