"""Minimal Nelder-Mead (scipy is not in the venv)."""
import numpy as np


def nelder_mead(f, x0, step=None, maxiter=3000, xatol=1e-3, fatol=1e-7):
    x0 = np.asarray(x0, float); n = len(x0)
    step = np.full(n, 0.5) if step is None else np.asarray(step, float)
    S = [x0] + [x0 + np.eye(n)[i] * step[i] for i in range(n)]
    F = [f(s) for s in S]
    for it in range(maxiter):
        o = np.argsort(F); S = [S[i] for i in o]; F = [F[i] for i in o]
        if max(np.abs(S[i] - S[0]).max() for i in range(1, n + 1)) < xatol and abs(F[-1] - F[0]) < fatol:
            break
        c = np.mean(S[:-1], axis=0)
        xr = c + (c - S[-1]); fr = f(xr)
        if fr < F[0]:
            xe = c + 2 * (c - S[-1]); fe = f(xe)
            S[-1], F[-1] = (xe, fe) if fe < fr else (xr, fr)
        elif fr < F[-2]:
            S[-1], F[-1] = xr, fr
        else:
            xc = c + 0.5 * (S[-1] - c); fc = f(xc)
            if fc < F[-1]:
                S[-1], F[-1] = xc, fc
            else:
                S = [S[0]] + [S[0] + 0.5 * (s - S[0]) for s in S[1:]]
                F = [F[0]] + [f(s) for s in S[1:]]
    i = int(np.argmin(F))
    return S[i], F[i]
