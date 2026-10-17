import numpy as np
HF = 1 / 2.5614  # Blender auto-handle time fraction for F-curves (fcurve_smoothing NONE)


def seg_u(t, t0, t1, h):
    L = t1 - t0
    P0, P1, P2, P3 = t0, t0 + h * L, t1 - h * L, t1
    a = -P0 + 3 * P1 - 3 * P2 + P3
    b = 3 * P0 - 6 * P1 + 3 * P2
    c = -3 * P0 + 3 * P1
    d = P0 - t
    lo = np.zeros_like(t)
    hi = np.ones_like(t)
    for _ in range(50):
        m = (lo + hi) / 2
        f = ((a * m + b) * m + c) * m + d
        lo = np.where(f < 0, m, lo)
        hi = np.where(f < 0, hi, m)
    return (lo + hi) / 2


def basis(times, tq, rules, h=HF):
    """value(tq) = B @ key_values for a Blender Bezier F-curve with auto(-clamped) handles.
    rules[k]: 'flat' (endpoint / extremum) or 'avg' (slope = mean of adjacent chord slopes)."""
    times = np.asarray(times, float)
    tq = np.asarray(tq, float)
    K = len(times)
    S = np.zeros((K, K))
    for k in range(K):
        if rules[k] == 'avg':
            la = times[k] - times[k - 1]
            lb = times[k + 1] - times[k]
            S[k, k] += (1 / la - 1 / lb) / 2
            S[k, k - 1] += -1 / la / 2
            S[k, k + 1] += 1 / lb / 2
    B = np.zeros((len(tq), K))
    B[tq <= times[0], 0] = 1
    B[tq >= times[-1], -1] = 1
    for k in range(K - 1):
        m = (tq >= times[k]) & (tq < times[k + 1]) & (tq > times[0])
        if not m.any():
            continue
        L = times[k + 1] - times[k]
        u = seg_u(tq[m], times[k], times[k + 1], h)
        w0 = (1 - u) ** 3
        w1 = 3 * u * (1 - u) ** 2
        w2 = 3 * u ** 2 * (1 - u)
        w3 = u ** 3
        rows = np.zeros((m.sum(), K))
        rows[:, k] += w0 + w1
        rows += np.outer(w1 * h * L, S[k])
        rows[:, k + 1] += w2 + w3
        rows -= np.outer(w2 * h * L, S[k + 1])
        B[m] = rows
    return B
