"""Ballistic (constant-g) 3D fits of lab objects in free flight. Test inputs only (dense pixel tracks from
runs/_dense_cache/test, depth_info ranges, fixed lab camera f = 722 px at 1280 px, capture clock 25 fps with the frames
dropped after video frames 11/35/59 put back).

Model: P(tau) = P0 + V0 s + 0.5 G s^2 (s = tau - tau_m), fitted to the per-frame viewing rays (reprojection error, px)
and the stated ranges (cm-level weight). G has fixed magnitude 9.8 (direction free) or is fully free (kill test:
|G| must come out near 9.8 if pixels, f, ranges and clock are consistent).
Label emulation (lab): speed(t) = |P(t + 1/25) - P(t)| * 25 (forward difference of the 25 fps clicked centres),
displacement = |P(t2) - P(t1)|.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np


class _Res:
    def __init__(self, x, cost):
        self.x, self.cost = x, cost


def least_squares(fun, x0, max_nfev=4000, **_):
    """Levenberg-Marquardt with a forward-difference Jacobian (numpy only; scipy is not installed)."""
    x = np.asarray(x0, float).copy()
    r = fun(x); cost = 0.5 * r @ r; lam = 1e-3
    for _ in range(300):
        J = np.empty((len(r), len(x)))
        for j in range(len(x)):
            h = 1e-6 * max(1.0, abs(x[j]))
            xh = x.copy(); xh[j] += h
            J[:, j] = (fun(xh) - r) / h
        A = J.T @ J; g = J.T @ r
        improved = False
        for _ in range(20):
            try:
                dx = -np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-12), g)
            except np.linalg.LinAlgError:
                lam *= 10; continue
            rn = fun(x + dx); cn = 0.5 * rn @ rn
            if cn < cost:
                x, r, lam = x + dx, rn, max(lam / 3, 1e-9)
                improved = abs(cost - cn) > 1e-12 * max(cost, 1e-12)
                cost = cn
                break
            lam *= 4
        if not improved:
            break
    return _Res(x, cost)

ROOT = Path(__file__).resolve().parents[2]
F = 722.0
CX, CY = 640.0, 359.5
FPS_CAP = 25.0
G0 = 9.8


def tau_of_frame(n):
    n = np.asarray(n)
    return (n + (n >= 12) + (n >= 36) + (n >= 60)) / FPS_CAP


def dense_paths(video_id: str) -> list[dict[int, tuple[float, float]]]:
    d = json.loads((ROOT / f"runs/_dense_cache/test/{video_id}.json").read_text())
    return [{int(k): tuple(v) for k, v in e["path"].items()} for e in d.values()]


def rays(uv):
    uv = np.asarray(uv, float)
    d = np.c_[(uv[:, 0] - CX) / F, (uv[:, 1] - CY) / F, np.ones(len(uv))]
    return d / np.linalg.norm(d, axis=1, keepdims=True)


def project(P):
    return np.c_[CX + F * P[:, 0] / P[:, 2], CY + F * P[:, 1] / P[:, 2]]


def _dir(th, ph):
    return np.array([math.sin(th) * math.cos(ph), math.cos(th), math.sin(th) * math.sin(ph)])


class Fit:
    def __init__(self, tau, uv, ranges, free_g=False, sig_px=3.0, sig_r=0.01):
        self.tau = np.asarray(tau, float)
        self.uv = np.asarray(uv, float)
        self.ranges = [(float(t), float(r)) for t, r in ranges]
        self.tm = float(np.mean(self.tau))
        self.free_g = free_g
        self.sig_px, self.sig_r = sig_px, sig_r
        self._solve()

    def pos(self, tau, p=None):
        p = self.p if p is None else p
        P0, V0 = p[0:3], p[3:6]
        G = p[6:9] if self.free_g else G0 * _dir(p[6], p[7])
        s = np.asarray(tau, float)[..., None] - self.tm
        return P0 + V0 * s + 0.5 * G * s ** 2

    def G(self):
        return self.p[6:9] if self.free_g else G0 * _dir(self.p[6], self.p[7])

    def _res(self, p):
        P = self.pos(self.tau, p)
        r = list(((project(P) - self.uv) / self.sig_px).ravel())
        for t, rr in self.ranges:
            r.append((np.linalg.norm(self.pos(np.array([t]), p)[0]) - rr) / self.sig_r)
        return np.array(r)

    def _solve(self):
        rr = np.median([r for _, r in self.ranges])
        P = rays(self.uv) * rr
        A = np.c_[np.ones_like(self.tau), self.tau - self.tm, 0.5 * (self.tau - self.tm) ** 2]
        c, *_ = np.linalg.lstsq(A, P, rcond=None)
        best = None
        for th0 in (0.05, 0.4, 0.8):
            for ph0 in (-1.5, 0.0, 1.5, 3.1):
                g0 = list(G0 * _dir(th0, ph0)) if self.free_g else [th0, ph0]
                if self.free_g:
                    g0 = list(c[2]) if (th0, ph0) == (0.05, 0.0) else g0
                p0 = np.r_[c[0], c[1], g0]
                try:
                    s = least_squares(self._res, p0)
                except Exception:
                    continue
                if best is None or s.cost < best.cost:
                    best = s
        self.p = best.x
        res = self._res(self.p)
        npx = 2 * len(self.tau)
        self.rms_px = float(np.sqrt(np.mean((res[:npx] * self.sig_px) ** 2)))
        self.range_err = [float(x * self.sig_r) for x in res[npx:]]

    def speed_fd(self, t):
        P = self.pos(np.array([t, t + 1 / FPS_CAP]))
        return float(np.linalg.norm(P[1] - P[0]) * FPS_CAP)

    def speed_inst(self, t):
        p = self.p
        G = self.G()
        return float(np.linalg.norm(p[3:6] + G * (t - self.tm)))

    def disp(self, t1, t2):
        P = self.pos(np.array([t1, t2]))
        return float(np.linalg.norm(P[1] - P[0]))


def segment(path: dict[int, tuple], f0: int, f1: int):
    fr = [f for f in sorted(path) if f0 <= f <= f1]
    return tau_of_frame(np.array(fr)), np.array([path[f] for f in fr]), fr
