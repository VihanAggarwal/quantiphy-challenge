"""Geometry solver: pixel tracks + one known quantity -> the answer in the asked unit.

    from qp.geometry import solve
    ans = solve(spec, tracks, image_size=(width, height), fps=fps)

2D: one image-plane scale s [m/px] = prior_SI / prior measured on its track in px, px/s or
px/s^2 (time is known, so one length scale serves every kind).

3D (spec.is_3d and depth entries): pinhole camera, principal point at the image centre, unknown
focal length f [px]. A depth_info distance is the object's Euclidean range r (DEPTH_IS_RANGE;
else optical-axis Z): pixel (u, v) back-projects to P = Z * ray, ray = ((u-cx)/f, (v-cy)/f, 1),
Z = r/|ray|. Sizes are fronto-parallel at depth Z: L = len_px * Z / f. Entries match objects by fuzzy name
(match_depth) and are linearly inter/extrapolated in time. f is solved (log-f scan + bisection)
so the prior computed in 3D equals its value; the target uses its own range, so radial motion
counts. Missing depths are flagged: prior -> scene median range; target -> target2's, else the
prior's median range, else the scene median. Bad or missing f -> 60 deg FOV. A prior that hardly
depends on f (motion along the line of sight, |d ln q / d ln f| < 0.3) is flagged
"f_ill_conditioned" and its f kept only within 25-100 deg FOV.

Motion: robust (outlier-dropping) local polynomial fits of position vs time, degree 2, raised to
3-4 only when an F-test says the extra terms pay off (curved paths):
  speed at t        |v(t)| of the fit to the obs within +-0.5 s (at least the 5 nearest)
  speed + window    |p(t1) - p(t0)| / (t1 - t0) (average velocity) from fitted positions
  speed, no time    path length / duration (average *speed*: right for orbits and turns)
  acceleration      2nd derivative of a degree-2 fit: over the window if given; at a time t over
                    the widest of (track, +-1.5 s, +-0.75 s) needing degree < 4; else over the
                    longest run one parabola fits (free flight; skips holds, bounces, catches)
  displacement      |p(t1) - p(t0)|;   path_length = summed segments of the fitted path
  distance          |p_a(t) - p_b(t)|; time None -> median over common times, inf -> last frame
                    (both tracks required; a one-object "distance" is its extent length)
  size              extent length (else box side), median over obs (or obs within +-0.5 s of t)
Quantity.axis "vertical"/"horizontal" keeps only y / x (3D: x and z). Gravity priors are vertical
and, with no prior track, try the target's track; with a gravity prior a mean speed is taken over
the free flight only. A motion prior must stand well out of its track's noise (else
"prior_motion_below_noise": a static or wrongly tracked prior would give a huge scale). Times
outside a track are clamped to it (flag "time_outside_track"; +-inf means last / first frame).

solve() never raises: unsolvable inputs give Answer(value=None, flags=[reason]).
"""

from __future__ import annotations

import math
import re
import warnings
from dataclasses import replace
from difflib import SequenceMatcher

import numpy as np

from qp.parse import _UNITS, canonical_unit
from qp.spec import KIND_DIM, Answer, DepthEntry, Obs, Quantity, QuestionSpec, RoleTrack

DEPTH_IS_RANGE = True           # depth_info = Euclidean camera range (False: optical-axis Z)
DEFAULT_FOV_DEG = 60.0          # horizontal FOV assumed when f cannot be solved from the prior
FOV_RANGE_DEG = (4.0, 130.0)    # a solved f outside this horizontal FOV is rejected
SPEED_HALF_WIN = 0.5            # s, half-width of local fits for position / velocity
ACC_HALF_WIN = 0.75             # s, narrowest half-width for acceleration at t (wider if parabolic)
MIN_LOCAL_OBS = 5               # a local fit uses at least this many obs (nearest in time)
DEG_F = 2.0                     # local fits keep a higher-degree term when its F statistic exceeds
                                # this: dropping it costs bias^2 ~ (F-1) x the variance it adds
DEPTH_MATCH_MIN = 0.5           # minimum name score to use a depth_info entry for an object
NAME_STRICT = 0.6               # track-by-name for a two-object distance: one shared word of two
                                # ("black ball" vs "ball") is another instance, not a match
SNR_MIN = 5.0                   # a prior's motion must exceed SNR_MIN x its noise (see _motion)
PX_NOISE_FLOOR = 0.5            # px, least noise assumed on a track (noise-free / quantised input)
GRAVITY_BORROW_MIN = 6          # obs needed to try the target's own track as the falling object
F_SENS_MIN = 0.3                # |d ln(prior) / d ln f| below this: f is ill-conditioned ...
FOV_ILL_RANGE_DEG = (25.0, 100.0)  # ... and then kept only within this horizontal FOV
FRAME_WIDTH_RANGE_M = (1e-4, 1e5)  # 2D: a scale making the frame width leave this range is rejected


class _Fail(Exception):
    """Unsolvable input; the message becomes an Answer flag."""


def _num(x, inf_ok: bool = False) -> float | None:
    """float(x), or None if missing / NaN / non-numeric (and +-inf unless inf_ok)."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) or (inf_ok and not math.isnan(v)) else None


def _arr(x, n: int) -> np.ndarray | None:
    try:
        a = np.asarray(x, dtype=float).reshape(-1)
    except (TypeError, ValueError):
        return None
    return a if a.size == n and np.isfinite(a).all() else None


# ------------------------------------------------------------------ observations

class _Obj:
    """Cleaned pixel observations of one tracked object (finite values only, sorted by t)."""

    def __init__(self, track: RoleTrack, flags: set[str]):
        self.name, self.flags, self.rows = str(track.object or ""), flags, []
        for o in track.obs or []:
            o = Obs(**o) if isinstance(o, dict) else o
            t = _num(getattr(o, "t", None))
            if t is not None:
                self.rows.append((t, _arr(o.point, 2), _arr(o.extent, 4), _arr(o.box, 4)))
        self.rows.sort(key=lambda r: r[0])

    def points(self) -> tuple[np.ndarray, np.ndarray]:
        """(t, uv) motion reference points: Obs.point if the track has any, else box centres,
        else extent midpoints (never mixed within one track)."""
        for i, flag in ((1, ""), (3, "point_from_box"), (2, "point_from_extent")):
            got = [(r[0], r[i] if i == 1 else (r[i][:2] + r[i][2:]) / 2) for r in self.rows
                   if r[i] is not None]
            if got:
                if flag:
                    self.flags.add(flag)
                return np.array([g[0] for g in got]), np.array([g[1] for g in got])
        return np.zeros(0), np.zeros((0, 2))

    def lengths(self, dimension: str, box: bool = True) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """(t, midpoint uv, length px) per obs: extent length, else (if `box`) the box side picked
        by `dimension` (height -> h, width -> w, anything else -> max(w, h))."""
        out = [(r[0], (r[2][:2] + r[2][2:]) / 2, math.hypot(*(r[2][2:] - r[2][:2])))
               for r in self.rows if r[2] is not None]
        if not out and box:
            d = (dimension or "").lower()
            side = ((lambda w, h: h) if re.search(r"height|tall|vertical", d) else
                    (lambda w, h: w) if re.search(r"width|wide|breadth|horizontal", d) else max)
            out = [(r[0], (r[3][:2] + r[3][2:]) / 2, side(abs(r[3][2] - r[3][0]), abs(r[3][3] - r[3][1])))
                   for r in self.rows if r[3] is not None]
            if out:
                self.flags.add("size_from_box")
        out = [o for o in out if o[2] > 0]
        return (np.array([o[0] for o in out]), np.array([o[1] for o in out]).reshape(-1, 2),
                np.array([o[2] for o in out]))


class _View:
    """Pixel -> working coordinates: identity (2D, rng None) or metric back-projection (3D)."""

    def __init__(self, f: float | None = None, c=(0.0, 0.0), rng=None):
        self.f, self.c, self.rng = f, np.asarray(c, float), rng

    def _ray_norm(self, uv: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        ray = np.column_stack([(uv - self.c) / self.f, np.ones(len(uv))])
        return ray, np.linalg.norm(ray, axis=1)

    def _depth(self, t: np.ndarray, uv: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """(ray with z=1, optical-axis depth Z) per point."""
        ray, n = self._ray_norm(uv)
        return ray, self.rng(t) / (n if DEPTH_IS_RANGE else 1.0)

    def pos(self, t: np.ndarray, uv: np.ndarray) -> np.ndarray:
        if self.rng is None:
            return uv
        ray, z = self._depth(t, uv)
        return ray * z[:, None]

    def length(self, t: np.ndarray, mid: np.ndarray, length_px: np.ndarray) -> np.ndarray:
        if self.rng is None:
            return length_px
        return length_px * self._depth(t, mid)[1] / self.f

    def per_px(self, t: np.ndarray, uv: np.ndarray) -> float:
        """Working units per pixel (1 in 2D, ~Z/f metres in 3D), median over the points."""
        return 1.0 if self.rng is None else float(np.median(self._depth(t, uv)[1] / self.f))


# ------------------------------------------------------------------ fitting

def _polyfit(x: np.ndarray, Y: np.ndarray, deg: int, iters: int = 3, k: float = 3.0):
    """Least-squares polynomial per column (highest power first, shape (deg+1, d)), refit after
    dropping points whose residual norm exceeds k robust sigmas -> (coefficients, inlier mask)."""
    keep = np.ones(len(x), bool)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for _ in range(iters):
            c = np.polyfit(x[keep], Y[keep], deg)
            r = np.linalg.norm(Y - np.vander(x, deg + 1) @ c, axis=1)
            new = r <= max(k * 1.4826 * np.median(r[keep]), 1e-9 * (1.0 + np.abs(Y).max()))
            if new.sum() < deg + 2 or (new == keep).all():
                break
            keep = new
        else:
            c = np.polyfit(x[keep], Y[keep], deg)
    return c, keep


def _local(t: np.ndarray, P: np.ndarray, t0: float, half: float, max_deg: int = 3):
    """Robust fit to the obs near t0 -> (position, velocity, acceleration, degree, sigma, span,
    lever) at t0: sigma = residual noise per coordinate (0 with no spare dof), span = fitted time
    range, lever = standard errors of (position, velocity, acceleration) per unit sigma.

    Degree 2 unless enough obs (2 per coefficient) and an F-test say the higher terms pay
    off: a parabola is biased on curved paths (orbits, turns, varying acceleration), a
    higher degree only adds noise on true parabolas. Inliers come from the max-degree fit."""
    sel = np.abs(t - t0) <= half
    if sel.sum() < MIN_LOCAL_OBS:
        sel = np.zeros(len(t), bool)
        sel[np.argsort(np.abs(t - t0), kind="stable")[:MIN_LOCAL_OBS]] = True
    x, Y = t[sel] - t0, P[sel]
    nu = len(np.unique(x))
    deg = max(min(2, nu - 1), min(max_deg, (nu - 2) // 2))
    c, keep = _polyfit(x, Y, deg)
    xk, Yk = x[keep], Y[keep]
    rss = lambda cc: float(((Yk - np.vander(xk, len(cc)) @ cc) ** 2).sum())  # noqa: E731
    floor = 1e-12 * (1.0 + float((Yk ** 2).sum()))
    while deg > 2:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            lower = np.polyfit(xk, Yk, deg - 1)
        r_hi, r_lo = rss(c), rss(lower)
        if r_lo > floor and (r_lo - r_hi) * (len(xk) - deg - 1) > DEG_F * max(r_hi, 1e-300):
            break  # top term worth keeping
        c, deg = lower, deg - 1
    dof = (len(xk) - deg - 1) * P.shape[1]
    sigma = math.sqrt(rss(c) / dof) if dof > 0 else 0.0
    X = np.vander(xk, deg + 1)
    lever = np.sqrt(np.abs(np.diag(np.linalg.pinv(X.T @ X))))[::-1] * [1, 1, 2, 6, 24][:deg + 1]
    lever = np.r_[lever, np.full(3, np.inf)][:3]
    zero = np.zeros(P.shape[1])
    return (c[-1], (c[-2] if deg >= 1 else zero), (2 * c[-3] if deg >= 2 else zero), deg, sigma,
            float(np.ptp(xk)), lever)


def _parabolic_span(t: np.ndarray, Y: np.ndarray) -> slice:
    """Longest run of consecutive obs that one parabola fits to within the noise or 0.5% of the
    motion (free flight between a throw and a bounce or catch; the tolerance keeps small model
    errors, e.g. from depth interpolation, from splitting a good track). A partial run must bend
    visibly (sag a*T^2/8 > 3 tol), so a ball resting on the ground does not win."""
    n = len(t)
    if n < 10:
        return slice(0, n)
    sigma = np.median(np.linalg.norm(np.diff(Y, 2, axis=0), axis=1)) / 2.9  # white-noise level
    tol = max(3.0 * sigma, 0.005 * float(np.ptp(Y, axis=0).max()), 1e-9)  # or 0.5% of the motion
    cuts = np.unique(np.linspace(0, n, min(n, 24) + 1).round().astype(int))
    spans = sorted(((a, b) for a in cuts for b in cuts if b - a >= 8), key=lambda s: (s[0] - s[1], s[0]))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for a, b in spans:
            c = np.polyfit(t[a:b], Y[a:b], 2)
            r = np.linalg.norm(Y[a:b] - np.vander(t[a:b], 3) @ c, axis=1)
            sag = np.linalg.norm(2 * c[0]) * (t[b - 1] - t[a]) ** 2 / 8
            if np.sqrt(np.mean(r ** 2)) <= tol and (b - a == n or sag > 3 * tol):
                return slice(a, b)
    return slice(0, n)


def _axis_cols(axis: str, d: int) -> list[int]:
    a = (axis or "any").lower()
    if a.startswith("vert"):
        return [1]
    if a.startswith("hori"):
        return [0] if d == 2 else [0, 2]
    return list(range(d))


class _Clock:
    """Clamps query times into a track's span, flagging real (finite) out-of-range times."""

    def __init__(self, t: np.ndarray, tol: float, flags: set[str]):
        self.lo, self.hi, self.tol, self.flags = float(t[0]), float(t[-1]), tol, flags

    def __call__(self, x: float) -> float:
        if math.isfinite(x) and not self.lo - self.tol <= x <= self.hi + self.tol:
            self.flags.add("time_outside_track")
        return float(np.clip(x, self.lo, self.hi))


def _window(q: Quantity) -> tuple[float, float] | None:
    w = q.window
    if w is None or len(w) != 2 or _num(w[0]) is None or _num(w[1]) is None:
        return None
    return (float(min(w)), float(max(w)))


def _motion(q: Quantity, t: np.ndarray, P: np.ndarray, flags: set[str], tol: float,
            floor: float | None = None, flight: bool = False) -> float:
    """Speed / acceleration / displacement / path length of one object (working units).

    floor (a prior's measurement): its motion must exceed SNR_MIN x the noise, max(fit residual,
    floor) -- sag a*T^2/8 of an acceleration, |v| x fitted span, a displacement, or 2 SNR_MIN for
    the extent of a path -- and a velocity / acceleration SNR_MIN x its standard error, else _Fail:
    a near-static or non-parabolic prior track would give a huge scale.
    flight (gravity prior): a mean speed is taken over the longest parabolic run (free flight)."""
    if len(np.unique(t)) < 2:
        raise _Fail("too_few_obs")
    cols, win, time = _axis_cols(q.axis, P.shape[1]), _window(q), _num(q.time, inf_ok=True)
    if flight and q.kind == "speed" and time is None and not win:
        span = _parabolic_span(t, P)
        if span.stop - span.start < len(t):
            flags.add("parabolic_segment")
            t, P = t[span], P[span]
    at = _Clock(t, tol, flags)
    norm = lambda v: float(np.linalg.norm(np.asarray(v)[cols]))  # noqa: E731
    pos = lambda x: _local(t, P, at(x), SPEED_HALF_WIN)  # noqa: E731

    def check(signal: float, sigma: float, lever: float = 1.0, k: float = SNR_MIN) -> None:
        if floor is not None and not signal > k * max(sigma, floor) * lever:
            raise _Fail("prior_motion_below_noise")

    def path(t0: float, t1: float) -> float:  # summed segments of the fitted path
        fits = [_local(t, P, g, SPEED_HALF_WIN) for g in np.linspace(t0, t1, int(np.clip(len(t), 10, 60)))]
        pts = np.array([f[0][cols] for f in fits])
        check(float(np.ptp(pts, axis=0).max()), float(np.median([f[4] for f in fits])), k=2 * SNR_MIN)
        return float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum())

    def moved(t0: float, t1: float) -> float:  # |p(t1) - p(t0)|
        a, b = pos(t0), pos(t1)
        d = norm(b[0] - a[0])
        check(d, max(a[4], b[4]))
        return d

    if q.kind == "speed":
        if win:
            t0, t1 = at(win[0]), at(win[1])
            if t1 <= t0:
                raise _Fail("empty_window")
            return moved(t0, t1) / (t1 - t0)
        if time is not None:
            fit = pos(time)
            v = norm(fit[1])
            check(v * fit[5], fit[4])
            check(v, fit[4], fit[6][1])
            return v
        return path(at.lo, at.hi) / (at.hi - at.lo)
    if q.kind == "acceleration":
        if time is not None:  # widest window that a polynomial below degree 4 describes
            for half in (math.inf, 2 * ACC_HALF_WIN, ACC_HALF_WIN):
                fit = _local(t, P, at(time), half, max_deg=4)
                if fit[3] < 4:
                    break
        elif win:
            fit = _local(t, P, (at(win[0]) + at(win[1])) / 2, (at(win[1]) - at(win[0])) / 2, 2)
        else:  # constant acceleration (gravity, a stated prior): longest parabolic run
            span = _parabolic_span(t, P[:, cols])
            if span.stop - span.start < len(t):
                flags.add("parabolic_segment")
            ts = t[span]
            fit = _local(ts, P[span], (ts[0] + ts[-1]) / 2, math.inf, 2)
        if fit[3] < 2:
            raise _Fail("too_few_obs")
        a = norm(fit[2])
        check(a * fit[5] ** 2 / 8, fit[4])
        check(a, fit[4], fit[6][2])
        return a
    if q.kind in ("displacement", "path_length"):
        t0, t1 = (at(win[0]), at(win[1])) if win else (at.lo, at(time) if time is not None else at.hi)
        if q.kind == "displacement":
            return moved(t0, t1)
        if t1 <= t0:
            raise _Fail("empty_window")
        return path(t0, t1)
    raise _Fail(f"unsupported_kind:{q.kind}")


def _distance(q: Quantity, ta, Pa, tb, Pb, flags: set[str], tol: float) -> float:
    """|p_a(t) - p_b(t)| at q.time, or the median over the tracks' common times."""
    cols = _axis_cols(q.axis, Pa.shape[1])
    ca, cb = _Clock(ta, tol, flags), _Clock(tb, tol, flags)
    time = _num(q.time, inf_ok=True)
    if time is not None:
        times = np.array([time])
    else:
        times = ta[(ta >= cb.lo - tol) & (ta <= cb.hi + tol)]
        if not len(times):
            flags.add("no_common_times")
            times = ta
    pos_a = lambda x: _local(ta, Pa, ca(x), SPEED_HALF_WIN)[0]  # noqa: E731
    pos_b = lambda x: _local(tb, Pb, cb(x), SPEED_HALF_WIN)[0]  # noqa: E731
    d = [np.linalg.norm((pos_a(x) - pos_b(x))[cols]) for x in times]
    return float(np.median(d))


def _measure(q: Quantity, a: _Obj | None, b: _Obj | None, va: _View, vb: _View,
             flags: set[str], tol: float, role: str, flight: bool = False) -> float:
    """Quantity `q` measured on track(s) a (and b) in the views' working units. A prior's motion
    must stand out of its noise (see _motion); a distance between two named objects needs both
    tracks (one named object: the length of its extent, never a box side)."""
    kind = q.kind if q.kind in KIND_DIM else "other"
    if kind == "camera_distance":
        raise _Fail(f"{role}_camera_distance_needs_depth")
    if a is None or not a.rows:
        raise _Fail(f"no_{role}_track")
    no_b = kind == "distance" and (b is None or not b.rows)
    if no_b and len(q.objects or []) >= 2:
        raise _Fail(f"no_{role}2_track")
    if kind in ("size", "other") or no_b:
        t, mid, L = a.lengths(q.dimension, box=not no_b)
        if not len(L):
            raise _Fail(f"no_{role}2_track" if no_b else f"no_{role}_size_obs")
        if no_b:
            flags.add("distance_from_extent")
        m = va.length(t, mid, L)
        time = _num(q.time, inf_ok=True)
        if time is None:
            return float(np.median(m))
        dt = np.abs(t - np.clip(time, t[0], t[-1]))
        return float(np.median(m[dt <= max(SPEED_HALF_WIN, dt.min())]))
    ta, uva = a.points()
    if not len(ta):
        raise _Fail(f"no_{role}_points")
    if kind == "distance":
        tb, uvb = b.points()
        if not len(tb):
            raise _Fail(f"no_{role}2_points")
        return _distance(q, ta, va.pos(ta, uva), tb, vb.pos(tb, uvb), flags, tol)
    floor = PX_NOISE_FLOOR * va.per_px(ta, uva) if role == "prior" else None
    return _motion(q, ta, va.pos(ta, uva), flags, tol, floor, flight)


# ------------------------------------------------------------------ depth

_STOP = {"the", "a", "an", "of", "and", "to", "from", "in", "on", "at", "with", "camera",
         "distance", "between", "object"}
_SYN = {"human": "person", "man": "person", "men": "person", "woman": "person", "women": "person",
        "people": "person", "pedestrian": "person", "boy": "person", "girl": "person",
        "player": "person", "walker": "person", "bike": "bicycle", "bycicle": "bicycle",
        "cyclist": "bicycle", "vehicle": "car", "automobile": "car"}


def _singular(w: str) -> str:
    if len(w) > 4 and w.endswith("ies"):
        return w[:-3] + "y"
    if len(w) > 4 and re.search(r"(?:s|x|z|ch|sh)es$", w):
        return w[:-2]
    return w[:-1] if len(w) > 3 and w.endswith("s") and not w.endswith(("ss", "us")) else w


def _tokens(name: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", str(name or "").lower())
    return [_SYN.get(s, s) for s in (_singular(w) for w in words if w not in _STOP)]


def _tok_eq(a: str, b: str) -> bool:
    return a == b or (min(len(a), len(b)) >= 5 and SequenceMatcher(None, a, b).ratio() >= 0.88)


def name_score(a: str, b: str) -> float:
    """Fuzzy object-name similarity in [0, 1]: token overlap (typos, plurals, synonyms such as
    human/person); with no shared token, the share of the shorter joined name found inside the
    longer one ("pingpong" vs "ping pong ball")."""
    A, B = dict.fromkeys(_tokens(a)), dict.fromkeys(_tokens(b))  # ordered sets
    if not A or not B:
        return 0.0
    m = sum(any(_tok_eq(x, y) for y in B) for x in A)
    score = m / (len(A) + len(B) - m)
    ja, jb = "".join(A), "".join(B)
    if m == 0 and min(len(ja), len(jb)) >= 4 and (ja in jb or jb in ja):  # compounds
        score = max(score, min(len(ja), len(jb)) / max(len(ja), len(jb)))
    return score


class DepthFn:
    """Range (m) of one object vs time from its depth_info entries: piecewise-linear in time
    with linear extrapolation when >= 2 timed entries, else constant. Averages tied matches."""

    def __init__(self, groups: list[tuple[str, list[tuple[float | None, float]]]]):
        self.names = [g[0] for g in groups]
        self.values = [d for g in groups for _, d in g[1]]
        self._parts = [self._interp(pairs) for _, pairs in groups]

    @staticmethod
    def _interp(pairs):
        timed: dict[float, list[float]] = {}
        for t, d in pairs:
            if t is not None:
                timed.setdefault(t, []).append(d)
        if len(timed) < 2:
            const = float(np.mean([d for _, d in pairs]))
            return lambda t: np.full(np.shape(t), const)
        ts = np.array(sorted(timed))
        ds = np.array([np.mean(timed[x]) for x in ts])
        s0, s1 = (ds[1] - ds[0]) / (ts[1] - ts[0]), (ds[-1] - ds[-2]) / (ts[-1] - ts[-2])

        def fn(t):
            t = np.asarray(t, float)
            out = np.interp(t, ts, ds)
            out = np.where(t < ts[0], ds[0] + s0 * (t - ts[0]), out)
            out = np.where(t > ts[-1], ds[-1] + s1 * (t - ts[-1]), out)
            return np.maximum(out, 0.2 * ds.min())
        return fn

    def __call__(self, t) -> np.ndarray:
        t = np.atleast_1d(np.asarray(t, float))
        return np.mean([p(t) for p in self._parts], axis=0)


def _depth_groups(entries: list[DepthEntry]) -> list[tuple[str, list[tuple[float | None, float]]]]:
    groups: dict[str, tuple[str, list]] = {}
    for e in entries or []:
        e = DepthEntry(**e) if isinstance(e, dict) else e
        d = _num(getattr(e, "distance_m", None))
        if d is None or d <= 0:
            continue
        key = " ".join(_tokens(e.object)) or str(e.object)
        groups.setdefault(key, (str(e.object), []))[1].append((_num(e.time), d))
    return list(groups.values())


def match_depth(names: list[str], entries) -> DepthFn | None:
    """Depth function for an object known by any of `names` (track / spec object names),
    from DepthEntry list `entries` (or pre-grouped entries); None if nothing matches."""
    groups = entries if entries and isinstance(entries[0], tuple) else _depth_groups(entries)
    best, picks = 0.0, []
    for g in groups:
        s = max((name_score(n, g[0]) for n in names if n), default=0.0)
        if s > best + 1e-9:
            best, picks = s, [g]
        elif s > 0 and abs(s - best) <= 1e-9:
            picks.append(g)
    return DepthFn(picks) if best >= DEPTH_MATCH_MIN else None


# ------------------------------------------------------------------ solver

def _solve_f(fn, value: float, width: float, f_def: float) -> float | None:
    """Focal length (px) with fn(f) == value: log-spaced scan for sign changes of
    log(fn/value), bisection on log f; among several roots the one closest to f_def."""
    def g(f: float) -> float:
        try:
            q = fn(f)
        except (_Fail, ValueError, FloatingPointError, np.linalg.LinAlgError):
            return math.nan
        return math.log(q / value) if q > 0 and math.isfinite(q) else math.nan

    half = width / 2
    fs = np.geomspace(half / math.tan(math.radians(85)), half / math.tan(math.radians(0.25)), 25)
    gs = [g(f) for f in fs]
    roots = []
    for i in range(len(fs) - 1):
        if not (math.isfinite(gs[i]) and math.isfinite(gs[i + 1])) or gs[i] * gs[i + 1] > 0:
            continue
        lo, hi, glo = math.log(fs[i]), math.log(fs[i + 1]), gs[i]
        for _ in range(20):
            mid = (lo + hi) / 2
            gm = g(math.exp(mid))
            if not math.isfinite(gm):
                break
            if (gm > 0) == (glo > 0):
                lo, glo = mid, gm
            else:
                hi = mid
        roots.append(math.exp((lo + hi) / 2))
    return min(roots, key=lambda f: abs(math.log(f / f_def))) if roots else None


def _fov(f: float, width: float) -> float:
    return math.degrees(2 * math.atan(width / 2 / f))


def _const(v: float):
    return lambda t: np.full(np.shape(np.atleast_1d(t)), float(v))


def _sensitivity(fn, f: float) -> float:
    """|d ln fn / d ln f| at f (1 for sizes and sideways motion, ~0 for motion along the line of
    sight, where errors in the depths or the prior value get amplified 1/s times in f)."""
    try:
        return abs(math.log(fn(f * 1.05) / fn(f / 1.05))) / (2 * math.log(1.05))
    except (_Fail, ValueError, ZeroDivisionError, FloatingPointError):
        return math.nan


def _solve_3d(target, prior, pa, pb, ta, tb, groups, image_size, flags, debug, tol, flight=False):
    """3D answer in SI: focal length from the prior (see module docstring), then the target."""
    W, H = (_num(x) for x in image_size)
    if not W or not H or W <= 0 or H <= 0:
        raise _Fail("bad_image_size")
    c = (W / 2, H / 2)
    z_med = float(np.median([np.median([d for _, d in g[1]]) for g in groups]))

    def depth(obj, names, label):
        fn = match_depth([obj.name if obj else "", *names], groups)
        if fn is not None:
            debug[f"depth_{label}"] = fn.names
        return fn

    rpa = depth(pa, prior.objects[:1], "prior")
    rpb = depth(pb, prior.objects[1:2], "prior2") or rpa
    prior_has_depth = rpa is not None
    if not prior_has_depth:
        flags.add("prior_depth_assumed_scene_median")
        rpa = rpb = _const(z_med)

    f_def = (W / 2) / math.tan(math.radians(DEFAULT_FOV_DEG) / 2)
    f, method = None, "3d_default_focal"
    try:
        def fn(f: float) -> float:
            return _measure(prior, pa, pb, _View(f, c, rpa), _View(f, c, rpb), set(), tol, "prior")

        fn(f_def)  # structural failures (missing track, too few obs, prior below noise) surface here
        f = _solve_f(fn, prior.value_si, W, f_def)
        fov_ok = FOV_RANGE_DEG
        if f is not None:
            debug["f_sensitivity"] = sens = _sensitivity(fn, f)
            if sens < F_SENS_MIN:  # mostly radial motion prior: trust f only near usual cameras
                flags.add("f_ill_conditioned")
                fov_ok = FOV_ILL_RANGE_DEG
        if f is None:
            flags.add("f_solve_failed")
        elif not fov_ok[0] <= _fov(f, W) <= fov_ok[1]:
            flags.add("f_implausible")
            debug["f_rejected"] = f
            f = None
        else:
            method = "3d_focal_from_prior" if prior_has_depth else "3d_focal_assumed_depth"
            debug["prior_measured_si"] = _measure(prior, pa, pb, _View(f, c, rpa), _View(f, c, rpb),
                                                  flags, tol, "prior")
    except _Fail as e:
        flags.add(str(e))
    if f is None:
        flags.add("default_focal")
        f = f_def
    debug.update(f_px=f, fov_deg=_fov(f, W), scene_median_depth=z_med)

    rta = depth(ta, target.objects[:1], "target")
    rtb = depth(tb, target.objects[1:2], "target2")
    if rta is None and rtb is not None:
        flags.add("target_depth_from_target2")
        rta = rtb
    if rta is None:
        if prior_has_depth and pa is not None and pa.rows:
            flags.add("target_depth_from_prior")
            rta = _const(np.median(rpa(np.array([r[0] for r in pa.rows]))))
        else:
            flags.add("target_depth_scene_median")
            rta = _const(z_med)
    if rtb is None and tb is not None:
        flags.add("target2_depth_from_target")
    rtb = rtb or rta
    for key, obj, rng in (("prior", pa, rpa), ("target", ta, rta), ("target2", tb, rtb)):
        if obj is not None and obj.rows:  # median range used over the track, for debugging
            debug[f"range_{key}_m"] = float(np.median(rng(np.array([r[0] for r in obj.rows]))))
    value = _measure(target, ta, tb, _View(f, c, rta), _View(f, c, rtb), flags, tol, "target", flight)
    debug["target_measured_si"] = value
    return value, method


def _is_gravity(q: Quantity) -> bool:
    return q.kind == "acceleration" and (
        (q.axis or "").startswith("vert")
        or any(re.search(r"grav|free.?fall|^g$", str(o).lower()) for o in q.objects or []))


def _role(objs: dict[str, _Obj], role: str, names: list[str], flags: set[str], exclude=(),
          min_score: float = DEPTH_MATCH_MIN) -> _Obj | None:
    """Track for `role`, else the best name match (score >= min_score) among the other tracks."""
    if role in objs:
        return objs[role]
    cands = [(max((name_score(n, o.name) for n in names if n), default=0.0), r)
             for r, o in objs.items() if o not in exclude]
    if cands and max(cands)[0] >= min_score:
        flags.add(f"{role}_track_by_name")
        return objs[max(cands)[1]]
    return None


def _camera_distance(target: Quantity, ta: _Obj | None, groups, flags: set[str]) -> float:
    if not groups:
        raise _Fail("no_depth_info")
    fn = match_depth([ta.name if ta else "", *target.objects], groups)
    if fn is None:
        raise _Fail("no_depth_for_target")
    t = _num(target.time)
    return float(fn(t)[0]) if t is not None else float(np.median(fn.values))


def _to_unit(v: float, q: Quantity, flags: set[str]) -> float:
    unit = str(q.unit or "").strip()
    if not unit:
        return v
    cu = canonical_unit(unit)
    if cu not in _UNITS:
        flags.add("unknown_unit")
        return v
    scale, dim = _UNITS[cu]
    if dim != KIND_DIM.get(q.kind, "L"):
        flags.add("unit_kind_mismatch")
    return v / scale


def _solve(spec: QuestionSpec, tracks, image_size, fps, flags: set[str], debug: dict):
    fps = _num(fps)
    tol = max(2.0 / fps if fps and fps > 0 else 0.0, 0.1)
    objs: dict[str, _Obj] = {}
    for tr in tracks or []:
        tr = RoleTrack.from_dict(tr) if isinstance(tr, dict) else tr
        o, role = _Obj(tr, flags), str(tr.role).strip().lower()
        if o.rows and (role not in objs or len(o.rows) > len(objs[role].rows)):
            objs[role] = o
    target, prior = (replace(q, objects=[str(o) for o in q.objects or []]) for q in (spec.target, spec.prior))
    by_name = lambda q: NAME_STRICT if q.kind == "distance" else DEPTH_MATCH_MIN  # noqa: E731
    ta = _role(objs, "target", target.objects[:1], flags, min_score=by_name(target))
    tb = _role(objs, "target2", target.objects[1:2], flags, exclude=[ta], min_score=by_name(target))
    groups = _depth_groups(spec.depth)
    if target.kind == "camera_distance":
        return _camera_distance(target, ta, groups, flags), "depth_direct"
    if _num(prior.value_si) is None or prior.value_si <= 0:
        raise _Fail("no_prior_value")
    pa = _role(objs, "prior", prior.objects[:1], flags, min_score=by_name(prior))
    gravity = _is_gravity(prior)
    if gravity:  # no falling-object track: try the target's (the prior's noise check rejects a static one)
        prior = replace(prior, axis="vertical")
        if pa is None or len(pa.points()[0]) < 3:
            pa = next((o for o in (ta, tb) if o is not None and len(o.points()[0]) >= GRAVITY_BORROW_MIN), pa)
            if pa is not None:
                flags.add("gravity_from_target_track")
    pb = _role(objs, "prior2", prior.objects[1:2], flags, exclude=[pa], min_score=by_name(prior))
    debug["tracks"] = {r: len(o.rows) for r, o in objs.items()}
    if spec.is_3d and groups:
        return _solve_3d(target, prior, pa, pb, ta, tb, groups, image_size, flags, debug, tol, gravity)
    if spec.is_3d:
        flags.add("3d_without_depth")
    view = _View()
    p_px = _measure(prior, pa, pb, view, view, flags, tol, "prior")
    if not p_px > 0:
        raise _Fail("prior_measured_zero")
    scale = prior.value_si / p_px
    debug.update(prior_px=p_px, scale_m_per_px=scale)
    try:
        width = _num(image_size[0])
    except (TypeError, IndexError, KeyError):
        width = None
    if width and width > 0 and not FRAME_WIDTH_RANGE_M[0] <= width * scale <= FRAME_WIDTH_RANGE_M[1]:
        raise _Fail("scale_implausible")
    t_px = _measure(target, ta, tb, view, view, flags, tol, "target", gravity)
    debug["target_px"] = t_px
    return t_px * scale, "2d_scale"


def solve(spec: QuestionSpec, tracks: list[RoleTrack], image_size: tuple[int, int],
          fps: float) -> Answer:
    """Answer `spec` from pixel tracks. image_size is (width, height) of the ORIGINAL frames;
    the value is in spec.target.unit (SI when the unit is empty/unknown), None if unsolvable."""
    flags: set[str] = set()
    debug: dict = {}
    srcs = sorted({str((t.get("source") if isinstance(t, dict) else getattr(t, "source", "")) or "")
                   for t in tracks or []} - {""})
    qid = _num(getattr(spec, "qid", None))
    ans = Answer(qid=int(qid) if qid is not None else -1, value=None,
                 source="geometry" + (":" + "+".join(srcs) if srcs else ""))
    try:
        value_si, ans.method = _solve(spec, tracks, image_size, fps, flags, debug)
        value = _to_unit(value_si, spec.target, flags)
        if not (math.isfinite(value) and value > 0 and value_si > 1e-9):  # 1e-9 SI: numerically zero
            raise _Fail("invalid_value")
        ans.value, debug["value_si"] = float(value), float(value_si)
    except _Fail as e:
        flags.add(str(e))
    except Exception as e:  # never raise on bad input
        flags.add(f"error:{type(e).__name__}:{e}")
    ans.flags, ans.debug = sorted(flags), debug
    return ans
