"""Task 2/3 core: expected lab label given our answer and the object's motion geometry, and the MRA-optimal factor.

For a lab motion target (speed at t, path length, displacement; accelerations untouched) with Claude's target
track: the velocity direction / path shape / endpoints come from the capture-clock 3D track at the fixed camera,
the magnitude from OUR ANSWER A (assumed physical, log-normal error SIGMA_A), and labels are simulated with the
label-process emulator (labmodel.py) using the noise parameters fitted on the test priors (fit_noise.py).
factor = argmax_c E[MRA(c * A, label)] / argmax_c E[MRA(c * A, A * exp(-e))]: the label-process effect alone, with
the generic MRA shading for our own error divided out (downward shading was rejected on validation, PROBES.md).
Guards fixed a priori: accelerations untouched; near-static objects (A < MIN_SPEED m/s, or a path / displacement
under 3 cm, or a track that rests at the asked time / does not reach it) untouched, because the emulator's behaviour there (labels of a resting object = pure click noise) has no
support in the priors; total path lengths use only the frames where the object moves."""
import json
import os
from statistics import NormalDist
import numpy as np
from common import treal, track_real, local_fit, lateral_fraction, obj_class, motion_kind, HERE
import labmodel as LM

SIGMA_A = 0.15            # log-sd of our answer vs physical (a priori; not tuned on validation)
SIGMA_PX = 2.0
MIN_SPEED = 0.10          # m/s
MIN_LEN = 0.03            # m
MAX_OUTSIDE = 0.25        # s, an asked time further than this outside the target track is not modelled
_fit = json.load(open(HERE / "out" / "fit_noise.json"))
PARAMS = dict(sigma_px=SIGMA_PX, sigma_zb=float(os.environ.get("LABNOISE_SZB", _fit["2.0"]["sigma_zb"])), sigma_zL=float(_fit["2.0"]["sigma_zL"]))


def unit_scale(unit):
    u = str(unit or "").strip().lower()
    return 0.01 if u.startswith("cm") else 0.001 if u.startswith("mm") else 1.0


def sigma_z(cls, params):
    return params["sigma_zb"] if cls in ("small ball", "mid ball") else params["sigma_zL"]


def row_model(x, answer, unit, params=PARAMS, n=3000, seed=0, cap=None):
    """-> dict(kind, cls, sin_psi, factor, exp_ratio (mean label / A), med_ratio, gain) or None (no change)."""
    kind = motion_kind(x["question"])
    if kind not in ("speed", "path_length", "displacement"):
        return None
    c = x["cap"].get("target")
    if c is None or len(c["t"]) < 2 or not np.isfinite(answer) or answer <= 0:
        return None
    sp = x["spec"].target
    cls = obj_class(c["name"])
    sz = sigma_z(cls, params)
    A = float(answer) * unit_scale(unit)
    tr, P = track_real(c)
    rng = np.random.default_rng(seed)
    eps = SIGMA_A * np.array([NormalDist().inv_cdf((i + 0.5) / n) for i in range(n)])
    # our error: physical = A * exp(-eps), stratified normal, one draw per simulated label
    ratios = []
    win = [float(treal([w])[0]) for w in sp.window] if sp.window else None
    if kind == "speed":
        if A < MIN_SPEED:
            return None
        if win is not None:      # average speed over a window: path-like
            kind_eff = "path"
        else:
            t0 = float(treal([float(sp.time)])[0]) if sp.time is not None else float(tr[-1])
            if t0 < tr[0] - MAX_OUTSIDE or t0 > tr[-1] + MAX_OUTSIDE:   # asked time off the track: geometry unknown
                return None
            f = local_fit(tr, P, t0, 0.25)
            if f is None or np.linalg.norm(f[1]) < MIN_SPEED:          # the track says the object (nearly) rests
                return None
            pos, vel = f[0], f[1]
            u = vel / np.linalg.norm(vel)
            L = LM.speed_labels_s(pos, u[None] * (A * np.exp(-eps))[:, None], params["sigma_px"], sz, seed=seed + 1)
            ratios.append(L / A)
            out = dict(sin_psi=lateral_fraction(pos, vel))
            kind_eff = "speed"
    if kind in ("path_length", "displacement") or (kind == "speed" and win is not None):
        lo, hi = (win if win is not None else (float(tr[0]), float(tr[-1])))
        if hi - lo < 0.04:
            return None
        ts = np.arange(lo, hi + 1e-9, 1 / 25.0)
        if len(ts) < 2:
            return None
        fits = [local_fit(tr, P, ti, 0.25) for ti in ts]
        Q = np.array([f[0] for f in fits])
        if kind == "path_length" and win is None:   # total distance: the frames where the object moves
            spd = np.array([np.linalg.norm(f[1]) for f in fits])
            mv = np.where(spd >= max(0.25 * spd.max(), 0.05))[0]
            if len(mv) < 2:
                return None
            Q = Q[mv[0]:mv[-1] + 1]
        seg = np.linalg.norm(np.diff(Q, axis=0), axis=1)
        phys_path, phys_disp = seg.sum(), np.linalg.norm(Q[-1] - Q[0])
        dP = Q[-1] - Q[0]
        out = dict(sin_psi=lateral_fraction(np.median(Q, axis=0), dP) if np.linalg.norm(dP) > 0 else np.nan)
        if (A if kind != "speed" else A * (hi - lo)) < MIN_LEN:
            return None
        if kind == "displacement":
            if phys_disp <= 0:
                return None
            k = A * np.exp(-eps) / phys_disp
            Pab = np.stack([np.broadcast_to(Q[0], (n, 3)), Q[0] + k[:, None] * dP], axis=1)
            L = LM.path_labels_s(Pab, params["sigma_px"], sz, seed=seed + 1)
            ratios.append(L / A)
        else:
            if phys_path <= 0:
                return None
            Adist = A * (hi - lo) if kind == "speed" else A    # average speed -> distance over the window
            k = Adist * np.exp(-eps) / phys_path
            Qk = Q[0] + k[:, None, None] * (Q - Q[0])[None]
            L = LM.path_labels_s(Qk, params["sigma_px"], sz, seed=seed + 1)
            ratios.append(L / Adist)
        kind_eff = kind
    R = np.concatenate(ratios)
    fac_raw, sc, sc1 = LM.best_factor(R)
    R0 = np.exp(-eps)
    fac0, sc0, _ = LM.best_factor(R0)
    fac = round(fac_raw / fac0, 3)
    if cap:
        fac = min(fac, cap)
    sc_f = LM.mra(fac, R).mean()
    out.update(kind=kind, kind_eff=kind_eff, cls=cls, sigma_z=sz, factor=fac, factor_raw=fac_raw, shade0=fac0, gain=float(sc_f - sc1),
               exp_ratio=float(R.mean()), med_ratio=float(np.median(R)), speed_si=A)
    return out
