"""Shared helpers for the lab label-noise study (research/labnoise)."""
import math, pickle, re, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
FPS_CAP = 25.0           # lab capture rate; released clips are 24 fps with frames dropped after video frames 11/35/59
F1280 = 722.0            # fixed lab camera focal length at 1280 px width

# Table 6 of the QuantiPhy paper (measured prop sizes, m) for balls named in lab questions; "orange/white/green ball"
# have no stated size in Table 6 -> estimated from their tracks when needed
BALL_D = {"ping pong": 0.040, "pingpong": 0.040, "tennis": 0.067, "basketball": 0.232, "soccer": 0.175,
          "football": 0.175, "yoga": 0.522, "red ball": 0.07}


def tracks(split):
    return pickle.load(open(HERE / "out" / f"tracks_{split}.pkl", "rb"))


def treal(t, fps=24.0):
    """Video time (n/24) -> capture time (25 fps clock with the dropped frames put back)."""
    n = np.round(np.asarray(t, float) * fps).astype(int)
    return (n + (n >= 12) + (n >= 36) + (n >= 60)) / FPS_CAP


def interp_lin(x, xp, fp):
    """Linear interpolation with linear extrapolation at both ends."""
    xp = np.asarray(xp, float); fp = np.asarray(fp, float)
    if len(xp) == 1 or np.ptp(xp) == 0:
        return np.full(np.shape(x), fp[0])
    y = np.interp(x, xp, fp)
    lo, hi = x < xp[0], x > xp[-1]
    s0 = (fp[1] - fp[0]) / (xp[1] - xp[0]); s1 = (fp[-1] - fp[-2]) / (xp[-1] - xp[-2])
    y = np.where(lo, fp[0] + s0 * (x - xp[0]), y)
    return np.where(hi, fp[-1] + s1 * (x - xp[-1]), y)


def track_real(c):
    """Capture-clock 3D track of a captured qp.geometry track: (t_real, P) with the range re-read at the capture
    time of each frame (depth_info times taken as capture-clock times)."""
    t = np.asarray(c["t"], float); tr = treal(t)
    o = np.argsort(t); t, tr = t[o], tr[o]
    P = np.asarray(c["P"], float)[o]; rng = np.asarray(c["rng"], float)[o]
    u, ix = np.unique(t, return_index=True)
    r2 = interp_lin(tr, u, rng[ix])
    unit = P / np.linalg.norm(P, axis=1, keepdims=True)
    return tr, unit * r2[:, None]


def obj_class(name):
    n = (name or "").lower()
    if "ball" not in n:
        return "non-ball"
    for k, d in BALL_D.items():
        if k in n:
            return "large ball" if d >= 0.3 else ("mid ball" if d >= 0.15 else "small ball")
    return "small ball"   # coloured balls of the desk/floor sets (orange/white/green, ~7 cm)


def local_fit(t, P, t0, half=0.25, deg=2, min_n=5):
    """Quadratic least-squares fit of P(t) near t0 -> (position, velocity, acceleration) at t0."""
    t = np.asarray(t, float); P = np.asarray(P, float)
    sel = np.abs(t - t0) <= half
    if sel.sum() < min_n:
        sel = np.zeros(len(t), bool); sel[np.argsort(np.abs(t - t0))[:min_n]] = True
    x, Y = t[sel] - t0, P[sel]
    d = min(deg, len(np.unique(x)) - 1)
    if d < 1:
        return None
    c = np.polyfit(x, Y, d)
    pos = c[-1]; vel = c[-2]; acc = 2 * c[-3] if d >= 2 else np.zeros(P.shape[1])
    return pos, vel, acc


def lateral_fraction(pos, vel):
    """sin(psi): share of the velocity perpendicular to the viewing ray through pos."""
    r = pos / np.linalg.norm(pos)
    v = np.asarray(vel, float); sp = np.linalg.norm(v)
    if sp <= 0:
        return np.nan
    return float(np.linalg.norm(v - (v @ r) * r) / sp)


def mra_item(pred, gt):
    rel = abs(pred - gt) / gt
    return sum(rel < 1 - th for th in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95)) / 10.0


def motion_kind(question):
    q = question.lower()
    if "acceler" in q:
        return "acceleration"
    if re.search(r"distance travel|total distance|path length|distance (?:it|the \w+ )?(?:has )?travel", q):
        return "path_length"
    if "displacement" in q:
        return "displacement"
    if re.search(r"veloc|speed", q):
        return "speed"
    return None
