import numpy as np
class Sol: pass
def least_squares(fun, p0, method=None, iters=200):
    p = np.array(p0, float); lam = 1e-3
    r = fun(p); c = r @ r
    for it in range(iters):
        J = np.empty((len(r), len(p)))
        for j in range(len(p)):
            h = 1e-6 * max(1, abs(p[j])); q = p.copy(); q[j] += h
            J[:, j] = (fun(q) - r) / h
        A = J.T @ J; g = J.T @ r
        while True:
            dp = -np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-12), g)
            rn = fun(p + dp); cn = rn @ rn
            if cn < c:
                p = p + dp; lam = max(lam / 3, 1e-9); done = (c - cn) < 1e-12 * (1 + c); r, c = rn, cn; break
            lam *= 4
            if lam > 1e12: done = True; break
        if done: break
    s = Sol(); s.x = p; s.fun = r; s.jac = J; return s
