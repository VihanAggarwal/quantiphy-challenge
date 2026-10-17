import numpy as np
CX, CY = 640.0, 360.0
R_BALL = 0.0335
def ray(u, v, f):
    d = np.array([(u - CX) / f, (v - CY) / f, 1.0]); return d / np.linalg.norm(d)
def silhouette(C, R, f, n=720):
    """image points of the silhouette of a sphere centre C radius R"""
    C = np.asarray(C, float); d = np.linalg.norm(C); w = C / d
    a = np.cross(w, [0, 1, 0]); a /= np.linalg.norm(a); b = np.cross(w, a)
    s = R / d; rr = R * np.sqrt(1 - s * s); cc = C - w * R * s     # tangent circle centre (toward camera) and radius
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    P = cc[None] + rr * (np.cos(t)[:, None] * a + np.sin(t)[:, None] * b)
    return np.c_[f * P[:, 0] / P[:, 2] + CX, f * P[:, 1] / P[:, 2] + CY]
def extents(C, R, f):
    s = silhouette(C, R, f); return np.ptp(s[:, 0]), np.ptp(s[:, 1]), s.mean(0)
def centre_from_click(u, v, rng_surface, f, R=R_BALL):
    return ray(u, v, f) * (rng_surface + R)
