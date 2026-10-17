# Minimal Levenberg-Marquardt with a numeric Jacobian (scipy is not installed in the venv)
import numpy as np
class Res:
    pass
def least_squares(fun, x0, max_iter=400, tol=1e-12, **kw):
    x = np.asarray(x0, float).copy(); lam = 1e-3
    r = fun(x); c = 0.5 * r @ r
    for it in range(max_iter):
        J = np.empty((r.size, x.size))
        for j in range(x.size):
            h = 1e-6 * max(1.0, abs(x[j])); xp = x.copy(); xp[j] += h
            J[:, j] = (fun(xp) - r) / h
        A = J.T @ J; g = J.T @ r
        improved = False
        for _ in range(30):
            try: dx = -np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-12), g)
            except np.linalg.LinAlgError: lam *= 10; continue
            xn = x + dx; rn = fun(xn); cn = 0.5 * rn @ rn
            if np.isfinite(cn) and cn < c:
                improved = True; x, r = xn, rn; dc = c - cn; c = cn; lam = max(lam / 3, 1e-12); break
            lam *= 4
        if not improved or dc < tol * (1 + c): break
    s = Res(); s.x = x; s.cost = c; s.fun = r
    return s
