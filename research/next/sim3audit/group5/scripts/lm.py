import numpy as np
def least_squares(fun, x0, lo=None, hi=None, iters=300, eps=1e-6, steps=None):
    x = np.array(x0, float)
    lo = -np.inf * np.ones_like(x) if lo is None else np.array(lo, float)
    hi = np.inf * np.ones_like(x) if hi is None else np.array(hi, float)
    lam = 1e-3
    r = fun(x); cost = 0.5 * r @ r
    for it in range(iters):
        J = np.empty((r.size, x.size))
        for j in range(x.size):
            h = steps[j] if steps is not None else eps * max(1.0, abs(x[j]))
            xp = x.copy(); xp[j] += h
            J[:, j] = (fun(xp) - r) / h
        A = J.T @ J; g = J.T @ r
        improved = False
        for _ in range(20):
            try:
                dx = -np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-12), g)
            except np.linalg.LinAlgError:
                lam *= 10; continue
            xn = np.clip(x + dx, lo, hi)
            rn = fun(xn); cn = 0.5 * rn @ rn
            if np.isfinite(cn) and cn < cost:
                x, r, cost = xn, rn, cn; lam = max(lam / 3, 1e-12); improved = True; break
            lam *= 10
        if not improved or np.linalg.norm(dx) < 1e-10 * (1 + np.linalg.norm(x)): break
    class R: pass
    o = R(); o.x = x; o.cost = cost; o.fun = r
    return o
