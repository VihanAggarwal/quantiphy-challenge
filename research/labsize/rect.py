"""Planar rectangle reconstruction with a pinhole camera (test INPUTS only).

Four image corners of a planar rectangle (in order around it) and a focal length f give the 3D shape up to
scale: the corners are X_i = lam_i * d_i (d_i = K^-1 [u, v, 1]); a parallelogram has X1 + X3 = X2 + X4, three
linear equations in the four lam_i, so lam is the null vector. The reconstructed shape then gives
  - the aspect ratio (side 1-2 over side 2-3), independent of scale,
  - the corner angle, which is 90 deg only at the true f (a right-angle constraint on f),
  - metric sides once one 3D point of the plane (or one known length) fixes the scale.
"""
from __future__ import annotations

import math

import numpy as np


def rays(uv, f, c):
    uv = np.asarray(uv, float)
    return np.column_stack([(uv[:, 0] - c[0]) / f, (uv[:, 1] - c[1]) / f, np.ones(len(uv))])


def parallelogram(uv, f, c):
    """3D corners (scale: mean corner depth Z = 1) of the parallelogram whose image corners are uv (4x2)."""
    d = rays(uv, f, c)
    A = np.column_stack([d[0], -d[1], d[2], -d[3]])  # lam1 d1 - lam2 d2 + lam3 d3 - lam4 d4 = 0
    _, _, vt = np.linalg.svd(A)
    lam = vt[-1]
    lam = lam / np.sign(lam.sum())
    X = d * lam[:, None]
    return X / X[:, 2].mean()


def shape(uv, f, c):
    X = parallelogram(uv, f, c)
    a, b = np.linalg.norm(X[1] - X[0]), np.linalg.norm(X[2] - X[1])
    a2, b2 = np.linalg.norm(X[2] - X[3]), np.linalg.norm(X[3] - X[0])
    u, v = X[1] - X[0], X[3] - X[0]
    ang = math.degrees(math.acos(np.clip(u @ v / np.linalg.norm(u) / np.linalg.norm(v), -1, 1)))
    n = np.cross(u, v)
    n /= np.linalg.norm(n)
    return dict(X=X, s12=(a + a2) / 2, s23=(b + b2) / 2, aspect=(a + a2) / (b + b2), angle=ang, normal=n)


def f_right_angle(uv, c, fs=np.geomspace(400, 1400, 401)):
    """f values where the reconstructed corner angle crosses 90 deg (+ the angle curve)."""
    angs = np.array([shape(uv, f, c)["angle"] for f in fs])
    roots = []
    for i in range(len(fs) - 1):
        g0, g1 = angs[i] - 90, angs[i + 1] - 90
        if g0 == 0 or g0 * g1 < 0:
            roots.append(fs[i] + (fs[i + 1] - fs[i]) * g0 / (g0 - g1))
    return roots, fs, angs


def scale_to_point(X, P):
    """Scale factor making the plane of X (unit-scale corners) pass through 3D point P (camera frame)."""
    n = np.cross(X[1] - X[0], X[3] - X[0])
    n /= np.linalg.norm(n)
    # plane at scale s: n.(x - s X0) = 0 -> s = n.P / n.X0
    return float(n @ P / (n @ X[0]))


def metric(uv, f, c, s):
    X = parallelogram(uv, f, c) * s
    return X
