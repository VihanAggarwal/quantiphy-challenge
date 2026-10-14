"""Global penalised-spline derivative estimator for qp.geometry (a wrapper; qp/ is not edited).

Replaces the LOCAL derivative estimators of qp.geometry._motion
    speed at t          ICI-selected local polynomial (half-width 0.12..0.5 s), |v(t)|
    acceleration at t   widest local polynomial of degree < 4 (track, +-1.5 s, +-0.75 s), |a(t)|
by a GLOBAL fit of the whole track (Gemini's proposal):
    f(t) = sum_j c_j B_j(t), cubic B-splines on uniform knots (spacing D = T / K, K = clip(ceil(T / 0.04), 8, 60)),
    minimise   sum_i w_i |y_i - f(t_i)|^2 + lam * int f'''(t)^2 dt          (jerk penalty)
    For cubic B-splines f''' is constant on each knot interval and equals (third difference of c) / D^3, so
    int f'''^2 = |D3 c|^2 / D^5 exactly. The penalty's null space is the parabolas: with a large lam the fit is
    one constant-acceleration parabola (free flight is unbiased); a small lam follows the track.
    lam = rho * h^6 (rho = Huber-weighted obs per second): h is the equivalent-kernel time scale of an order-3 smoothing spline
    (Silverman 1984, h = (lam / rho)^(1/6)).
    w_i = Huber weights on residual norms standardised by their robust scale (1.4826 x median), k = 1.5,
    4 IRLS rounds (scale-free, i.e. relative to the track's own noise: "relative-error Huber").
    The coordinates share lam and the weights (one object).

Modes (FIXED BEFORE ANY EVALUATION; see RESULT.md):
    gcv        lam chosen per track by generalised cross-validation over h in geomspace(0.03, 3, 25) s
    h010       fixed h = 0.10 s
    h025       fixed h = 0.25 s (h = 0.40 was dropped before any evaluation: on a synthetic circle at 2 rad/s it
               shrinks speeds by 21%, transfer 1 / (1 + (w h)^6))
    gcv_glock  gcv, plus gravity lock: in 2D with a gravity prior, the speed at t of the prior's own (falling)
               track inside its free-flight span (qp.geometry._parabolic_span of the vertical coordinate, the
               span the prior's acceleration came from) takes its vertical velocity from that one parabola
               (vertical acceleration locked to the prior's), the horizontal one from the spline.

Everything else in qp.geometry is unchanged: the original _motion runs first (its prior noise checks, failures,
flags and every other kind: windows, untimed speeds, displacements, untimed accelerations), and only the value
of a speed or acceleration AT A TIME is replaced. Tracks with < 6 distinct times or a span < 0.2 s keep the
original value (flag spline_fallback).

    import spline
    with spline.patched("gcv"):
        ans = qp.geometry.solve(...)
"""
from __future__ import annotations

import contextlib
import contextvars
import math

import numpy as np

import qp.geometry as G

MODES = ("gcv", "h010", "h025", "gcv_glock")
KNOT_DT = 0.04          # s, target knot spacing
K_MIN, K_MAX = 8, 60    # number of knot intervals
GCV_H = np.geomspace(0.03, 3.0, 25)
HUBER_K = 1.5
IRLS_ROUNDS = 4
MIN_TIMES, MIN_SPAN = 6, 0.2

_ORIG_MOTION = G._motion
_ORIG_SOLVE = G.solve
_MODE: contextvars.ContextVar = contextvars.ContextVar("splinefit_mode", default=None)
_GRAV: contextvars.ContextVar = contextvars.ContextVar("splinefit_grav", default=None)
STATS = {"replaced": 0, "fallback": 0, "glock": 0}


# ------------------------------------------------------------------ cubic B-spline basis (uniform knots)

def _card(u: np.ndarray, der: int) -> np.ndarray:
    """Cardinal cubic B-spline N(u) on [0, 4) and its derivatives (der 0..3)."""
    out = np.zeros_like(u, dtype=float)
    p = [(u >= 0) & (u < 1), (u >= 1) & (u < 2), (u >= 2) & (u < 3), (u >= 3) & (u <= 4)]
    if der == 0:
        f = [lambda x: x ** 3 / 6, lambda x: (-3 * x ** 3 + 12 * x ** 2 - 12 * x + 4) / 6,
             lambda x: (3 * x ** 3 - 24 * x ** 2 + 60 * x - 44) / 6, lambda x: (4 - x) ** 3 / 6]
    elif der == 1:
        f = [lambda x: x ** 2 / 2, lambda x: (-3 * x ** 2 + 8 * x - 4) / 2,
             lambda x: (3 * x ** 2 - 16 * x + 20) / 2, lambda x: -(4 - x) ** 2 / 2]
    elif der == 2:
        f = [lambda x: x, lambda x: -3 * x + 4, lambda x: 3 * x - 8, lambda x: 4 - x]
    else:
        f = [lambda x: np.ones_like(x), lambda x: -3 * np.ones_like(x), lambda x: 3 * np.ones_like(x),
             lambda x: -np.ones_like(x)]
    for m, fn in zip(p, f):
        out[m] = fn(u[m])
    return out


class PSpline:
    """Robust penalised cubic spline fit of a track (t, Y[n, d])."""

    def __init__(self, t: np.ndarray, Y: np.ndarray, mode: str):
        o = np.argsort(t, kind="stable")
        self.t, self.Y = np.asarray(t, float)[o], np.asarray(Y, float)[o]
        self.lo, self.hi = float(self.t[0]), float(self.t[-1])
        T = self.hi - self.lo
        self.K = int(np.clip(math.ceil(T / KNOT_DT), K_MIN, K_MAX))
        self.D = T / self.K
        self.nb = self.K + 3
        B = self.basis(self.t, 0)
        D3 = np.diff(np.eye(self.nb), 3, axis=0)
        Pen = D3.T @ D3 / self.D ** 5
        n, d = self.Y.shape
        rho = n / T
        w = np.ones(n)
        hs = GCV_H if mode.startswith("gcv") else np.array([{"h010": 0.10, "h025": 0.25}[mode]])
        for _ in range(IRLS_ROUNDS):
            rho = float(w.sum()) / T            # weighted obs density: Huber weights must not add smoothing
            lams = rho * hs ** 6
            BW = B * w[:, None]
            BtWB, BtWY = BW.T @ B, BW.T @ self.Y
            best = None
            for lam in lams:
                A = BtWB + lam * Pen + 1e-12 * np.trace(BtWB) / self.nb * np.eye(self.nb)
                try:
                    c = np.linalg.solve(A, BtWY)
                except np.linalg.LinAlgError:
                    continue
                if len(lams) == 1:
                    best = (0.0, lam, c)
                    break
                r = self.Y - B @ c
                rss = float((w[:, None] * r ** 2).sum())
                edf = float(np.trace(np.linalg.solve(A, BtWB)))
                den = (n * d - d * edf)
                if den <= 0:
                    continue
                g = n * d * rss / den ** 2
                if best is None or g < best[0]:
                    best = (g, lam, c)
            if best is None:
                raise np.linalg.LinAlgError("no spline fit")
            self.lam, self.c = best[1], best[2]
            rn = np.linalg.norm(self.Y - B @ self.c, axis=1)
            s = 1.4826 * float(np.median(rn))
            if s <= 1e-9 * (1.0 + float(np.abs(self.Y).max())):
                break
            w_new = np.minimum(1.0, HUBER_K * s / np.maximum(rn, 1e-300))
            if np.allclose(w_new, w, atol=1e-4):
                break
            w = w_new
        self.h = (self.lam / rho) ** (1 / 6)

    def basis(self, x: np.ndarray, der: int) -> np.ndarray:
        x = np.atleast_1d(np.asarray(x, float))
        knots0 = self.lo - 3 * self.D + self.D * np.arange(self.nb)   # basis j lives on [knots0_j, knots0_j + 4D]
        u = (x[:, None] - knots0[None, :]) / self.D
        return _card(u, der) / self.D ** der

    def deriv(self, x: float, der: int) -> np.ndarray:
        x = float(np.clip(x, self.lo, self.hi))
        return (self.basis(np.array([x]), der) @ self.c)[0]


# ------------------------------------------------------------------ patch

def _same_track(a, b) -> bool:
    return a is not None and a[0].shape == b[0].shape and np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1])


def _motion_spline(q, t, P, flags, tol, floor=None, flight=False):
    v0 = _ORIG_MOTION(q, t, P, flags, tol, floor, flight)   # all checks / failures / other kinds unchanged
    mode = _MODE.get()
    if mode is None:
        return v0
    grav = _GRAV.get()
    if (mode == "gcv_glock" and grav is not None and floor is not None and P.shape[1] == 2
            and G._is_gravity(q) and grav.get("prior") is None):
        grav["prior"] = (np.asarray(t, float).copy(), np.asarray(P, float).copy())
    time = G._num(q.time, inf_ok=True)
    win = G._window(q)
    timed_speed = q.kind == "speed" and not win and time is not None
    timed_acc = q.kind == "acceleration" and time is not None
    if not (timed_speed or timed_acc):
        return v0
    tt = np.asarray(t, float)
    if len(np.unique(tt)) < MIN_TIMES or np.ptp(tt) < MIN_SPAN:
        flags.add("spline_fallback")
        STATS["fallback"] += 1
        return v0
    cols = G._axis_cols(q.axis, P.shape[1])
    try:
        fit = PSpline(tt, np.asarray(P, float), mode)
    except (np.linalg.LinAlgError, ValueError):
        flags.add("spline_fallback")
        STATS["fallback"] += 1
        return v0
    x = float(np.clip(time, fit.lo, fit.hi))
    if timed_speed:
        v = np.array(fit.deriv(x, 1), float)
        if (mode == "gcv_glock" and grav is not None and floor is None and P.shape[1] == 2
                and _same_track(grav.get("prior"), (tt, np.asarray(P, float)))):
            o = np.argsort(tt, kind="stable")
            ts, Ps = tt[o], np.asarray(P, float)[o]
            span = G._parabolic_span(ts, Ps[:, [1]])
            a, b = span.start, span.stop
            if b - a >= MIN_TIMES and ts[a] <= x <= ts[b - 1]:
                cy = np.polyfit(ts[a:b], Ps[a:b, 1], 2)
                v[1] = 2 * cy[0] * x + cy[1]
                flags.add("spline_glock")
                STATS["glock"] += 1
        val = float(np.linalg.norm(v[cols]))
    else:
        val = float(np.linalg.norm(np.array(fit.deriv(x, 2), float)[cols]))
    if not (math.isfinite(val) and val > 0):
        flags.add("spline_fallback")
        STATS["fallback"] += 1
        return v0
    flags.add("spline")
    STATS["replaced"] += 1
    return val


def _solve_wrapped(*a, **kw):
    token = _GRAV.set({})
    try:
        return _ORIG_SOLVE(*a, **kw)
    finally:
        _GRAV.reset(token)


@contextlib.contextmanager
def patched(mode: str | None):
    """Within the block qp.geometry uses the spline estimator `mode` (None: the original estimator).
    Callers that imported `solve` by name keep the original function object, which looks up _motion in
    qp.geometry's globals, so the patch reaches them too; the gravity-lock context needs G.solve or
    solve_ctx()."""
    if mode is not None and mode not in MODES:
        raise ValueError(mode)
    token = _MODE.set(mode)
    G._motion = _motion_spline
    G.solve = _solve_wrapped
    try:
        yield
    finally:
        G._motion = _ORIG_MOTION
        G.solve = _ORIG_SOLVE
        _MODE.reset(token)
