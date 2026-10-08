"""Agentic measurement loop (Track A): Claude Opus 5.5 measures one video's questions itself with
client-side tools, at pixel precision, then submits specs + pixel tracks + direct answers.

Pass 1 (qp.claude_annotate) reads positions off at most 32-44 whole frames in one shot. Here the model
works like an analyst at a workstation: it looks at overview frames, zooms into crops with tick labels
in ORIGINAL pixel units, tracks objects frame by frame, segments sizes, runs the geometry solver on its
own measurements and fixes what does not add up, then submits. The answers go through the same
contract as pass 1 (a records "parsed" JSON that qp.claude_annotate.to_annotations reads), so
scripts/run_claude.py's build_results / qp.combine selection applies unchanged.

Tools (all run locally; coordinates are always ORIGINAL video pixels, continuous: the pixel in column
j spans x = j..j+1; frame f is at t = f / dataset fps):
  get_frames(frames|times, region, zoom, marks, show, grid)  images with tick labels in original px on
                 the margins (qp.claude_verify's canvas); each image's text gives the exact mapping
                 original = region origin + (image px - margin) / zoom
  track(object, anchors=[{frame, box}], from_t, to_t)      dense per-frame box centre (qp.dense_track:
                 NCC template matching with anchor drift correction, dense_motion between >= 2 anchors;
                 a plain NCC tracker when dense_track is unavailable) -> stored measurement T<n>, a
                 compact table, quality numbers and an overlay
  segment(object, frame, box | extent, measure, method)  GrabCut mask -> extent along `measure` (long /
                 short axis, image horizontal / vertical, diameter; qp.open.cv_track.mask_features /
                 extent_from_features), its endpoints moved <= 2.5-4 px to the strongest edges (colour
                 bleeding of 4:2:0 video makes masks 1-2 px too large), or edge snapping of given endpoints
                 (qp.dense_track.snap_extent) -> stored measurement S<n> + overlay crop
  solve(qid, spec, tracks)       qp.geometry.solve on the spec + tracks (refs to T/S ids and/or manual
                 obs), normalised exactly like pass 1 (prior value / depth list from the text) -> answer
                 and intermediate numbers
  submit(answers=[{qid, spec, tracks | use_last_solve, direct_answer, confidence, derivation}])  ends

Loop (run_video): manual agentic loop on the Messages API, streamed; thinking is always on for Opus 5.5
and every assistant content list is appended back UNCHANGED (append-only history: the prompt-cache
prefix and the preserved-thinking prefix check both hold); tool_choice stays auto (forced tool use is
a 400 on Opus 5.5); tools are sorted, get_frames / segment / track strict (solve / submit are not: the
strict grammar allows 16 union-typed parameters per request, their nullable spec fields need 20; their
input is validated here); the system prompt carries an explicit cache
breakpoint and top-level automatic caching covers the growing tail (verify with
usage.cache_read_input_tokens). After each tool round a status line (turns / budget used) is appended
after the tool_result blocks (never edited later); near the turn cap or the per-video budget it asks
the model to submit. Hard stops: max_turns, the per-video USD cap (each request's max_tokens is
shrunk to fit it), an output-token cap, the global ledger cap (qp.budget.reserve at each request's
worst case). Questions without a submitted answer fall back to their last solve call.

    session = AgentSession(rows)                         # rows: one video's questions (qp.data)
    rec = run_video(client, session, AgentConfig(effort="medium", run="name", split="val"))
    rec["parsed"], rec["meta"]                           # -> qp.claude_annotate.to_annotations
"""

from __future__ import annotations

import base64
import copy
import hashlib
import json
import math
import time
from collections import Counter, OrderedDict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from . import budget
from . import claude_annotate as ca
from . import claude_verify as cvf
from . import combine

MODEL = ca.MODEL
AGENT_VERSION = "ag1"
ROLES = ca.ROLES
EFFORTS = ("low", "medium", "high", "xhigh", "max")

MAX_TURNS = 25            # API requests per video
TURN_MAX_TOKENS = 32000   # max_tokens per request (thinking + tool calls); streamed
MIN_TURN_TOKENS = 4000    # a request the per-video budget cannot give this many output tokens is not sent
MAX_USD_VIDEO = 2.0       # per-video cost cap
MAX_OUT_VIDEO = 200_000   # per-video output-token cap
WRAP_UP_FRAC = 0.7        # share of a per-video cap after which the status line asks for submit
WRAP_UP_TURNS = 2         # ... or when this few turns are left

OVERVIEW_FRAMES = 8       # uniform frames in the first message ...
OVERVIEW_EXTRA = 4        # ... plus up to this many frames at times the questions mention
OVERVIEW_SIDE = 1024      # long side of overview images (val 480p stays native)
VIEW_SIDE = 1024          # long side cap of every tool image
MAX_IMAGES = 8            # frames per get_frames call
MAX_ZOOM = 8.0
JPEG_QUALITY = 90
TRACK_ROWS = 30           # trajectory rows printed per track (all frames are stored)
WORK_SIDE = 1280          # tracking works on frames downscaled to this long side ...
WORK_BYTES = 6e8          # ... and further so the decoded range stays under this
FRAME_CACHE_BYTES = 1.2e9 # full-resolution frames kept per video (LRU)
TEMPLATE_MAX = 48         # px: tracking scales frames so the template's long side is at most this
GC_MIN_SIDE, GC_MAX_SIDE = 200, 600   # GrabCut crops are resized into this long-side range
GC_RECT_PAD = 0.08        # GrabCut seed rect = box padded by this share of its side (+1 px)
GC_FILL = (0.2, 0.97)     # mask area / seed rect area outside this: segmentation suspicious

# Rough cost model (offline estimate; replaced by observed per-question cost once a run has records)
EST_TURNS = {"low": 6, "medium": 8, "high": 10, "xhigh": 12, "max": 14}   # + 1 per question
EST_OUT_PER_TURN = {"low": 1200, "medium": 2000, "high": 3000, "xhigh": 4500, "max": 6000}
EST_IN_PER_TURN = 1500

COLORS = [(0, 0, 255), (255, 0, 255), (0, 170, 0), (255, 96, 0), (0, 140, 255), (255, 255, 0)]  # BGR: red, magenta, green, blue, orange, cyan
ML, MT = cvf.MARGIN_L, cvf.MARGIN_T


# --------------------------------------------------------------------------- small helpers

def _num(x) -> float | None:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def _r(v, nd: int = 2):
    return None if v is None else round(float(v), nd)


def _fmt(v: float) -> str:
    """Compact number: 4 significant digits."""
    return f"{v:.4g}" if v is not None and math.isfinite(v) else "nan"


def _jpeg_b64(img: np.ndarray) -> str:
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
    if not ok:
        raise RuntimeError("jpeg encode failed")
    return base64.b64encode(buf).decode()


def image_tokens(w: int, h: int) -> int:
    return math.ceil(w * h / 750)


def _odd(x: float, lo: int = 7) -> int:
    n = max(lo, int(round(x)))
    return n if n % 2 else n + 1


def _dense_track():
    """qp.dense_track, imported lazily (written in parallel; None if it cannot be imported)."""
    try:
        from . import dense_track
        return dense_track
    except Exception:  # noqa: BLE001
        return None


class ToolError(ValueError):
    """Bad tool input: returned to the model as an is_error tool_result."""


# --------------------------------------------------------------------------- video frames

class FrameStore:
    """Frames of one video: full resolution (LRU cache, sequential decode: exact for any codec) and
    downscaled frame ranges for tracking."""

    def __init__(self, path: str, n_frames: int, size: tuple[int, int], max_bytes: float = FRAME_CACHE_BYTES):
        self.path, self.n, self.size, self.max_bytes = path, n_frames, size, max_bytes
        self.cache: OrderedDict[int, np.ndarray] = OrderedDict()
        self.bytes = 0
        self.decodes = 0

    def get(self, idxs) -> dict[int, np.ndarray]:
        idxs = [int(i) for i in idxs]
        want = sorted({i for i in idxs if 0 <= i < self.n} - set(self.cache))
        if want:
            self._decode(want)
        out = {}
        for i in idxs:
            if i in self.cache:
                self.cache.move_to_end(i)
                out[i] = self.cache[i]
        return out

    def _decode(self, want: list[int]) -> None:
        self.decodes += 1
        cap = cv2.VideoCapture(self.path)
        if not cap.isOpened():
            raise FileNotFoundError(self.path)
        ws, hi, i = set(want), max(want), 0
        try:
            while i <= hi and cap.grab():
                if i in ws:
                    ok, img = cap.retrieve()
                    if ok:
                        self._put(i, img)
                i += 1
        finally:
            cap.release()

    def _put(self, i: int, img: np.ndarray) -> None:
        self.cache[i] = img
        self.bytes += img.nbytes
        while self.bytes > self.max_bytes and len(self.cache) > 1:
            _, old = self.cache.popitem(last=False)
            self.bytes -= old.nbytes

    def work(self, f0: int, f1: int, side: int = WORK_SIDE, max_bytes: float = WORK_BYTES) -> tuple[dict, float]:
        """({frame: BGR image} for f0..f1 downscaled to <= side (and <= max_bytes in total), scale =
        work px per original px)."""
        W, H = self.size
        n = max(1, f1 - f0 + 1)
        s = min(1.0, side / max(W, H, 1), math.sqrt(max_bytes / (3.0 * W * H * n)))
        wsize = (max(8, round(W * s)), max(8, round(H * s)))
        s = wsize[0] / W
        out: dict[int, np.ndarray] = {}
        cap = cv2.VideoCapture(self.path)
        if not cap.isOpened():
            raise FileNotFoundError(self.path)
        i = 0
        try:
            while i <= f1 and cap.grab():
                if i >= f0:
                    ok, img = cap.retrieve()
                    if not ok:
                        break
                    out[i] = img if wsize == (W, H) else cv2.resize(img, wsize, interpolation=cv2.INTER_AREA)
                i += 1
        finally:
            cap.release()
        return out, s


# --------------------------------------------------------------------------- rendering

@dataclass
class View:
    """One rendered image: original region [x0, x1) x [y0, y1) at `zoom`, with tick margins."""
    frame: int
    x0: int
    y0: int
    x1: int
    y1: int
    zoom: float
    img: np.ndarray

    def mapping(self) -> str:
        z = f"{self.zoom:.4g}"
        return (f"image px (u, v) -> original x = {self.x0} + (u - {ML}) / {z}, y = {self.y0} + (v - {MT}) / {z}")


def view_geometry(W: int, H: int, region=None, zoom=None, max_side: int = VIEW_SIDE) -> tuple[int, int, int, int, float]:
    """Integer region (clipped, at least 8 px) and zoom: requested zoom (default: the largest that fits
    max_side, at most MAX_ZOOM; full frames at most 1), capped to max_side; zooms >= 1 snap down to multiples of 0.5 with an
    even region side when the zoom is fractional, so the resize maps coordinates exactly."""
    if region is None:
        x0, y0, x1, y1 = 0, 0, W, H
    else:
        if not isinstance(region, (list, tuple)) or len(region) != 4 or any(_num(v) is None for v in region):
            raise ToolError("region must be [x1, y1, x2, y2] in original pixels")
        a, b, c, d = (float(v) for v in region)
        x0, x1 = sorted((a, c))
        y0, y1 = sorted((b, d))
        x0, y0 = max(0, int(math.floor(x0))), max(0, int(math.floor(y0)))
        x1, y1 = min(W, int(math.ceil(x1))), min(H, int(math.ceil(y1)))
        if x1 - x0 < 1 or y1 - y0 < 1:
            raise ToolError(f"region {region} is outside the {W}x{H} image")
        if x1 - x0 < 8:   # at least 8 px wide / high
            c = (x0 + x1) / 2
            x0, x1 = max(0, int(c - 4)), min(W, int(c - 4) + 8)
        if y1 - y0 < 8:
            c = (y0 + y1) / 2
            y0, y1 = max(0, int(c - 4)), min(H, int(c - 4) + 8)
    w, h = x1 - x0, y1 - y0
    zfit = max_side / max(w, h)
    zdef = min(MAX_ZOOM, zfit) if region is not None else min(1.0, zfit)   # full frames: never upscaled by default
    z = zdef if _num(zoom) is None or _num(zoom) <= 0 else min(float(zoom), MAX_ZOOM, zfit)
    if z >= 1:
        z = max(1.0, math.floor(z * 2) / 2)
        if z != int(z):
            if w % 2:
                x1, x0 = (x1 + 1, x0) if x1 < W else (x1, x0 - 1)
            if h % 2:
                y1, y0 = (y1 + 1, y0) if y1 < H else (y1, y0 - 1)
    return x0, y0, x1, y1, z


def render_view(img: np.ndarray, frame: int, region=None, zoom=None, max_side: int = VIEW_SIDE,
                grid: bool | None = None, draw=None) -> View:
    """Crop/zoom one frame onto a qp.claude_verify canvas; `draw(canvas)` adds marks before the tick
    margins are drawn."""
    H, W = img.shape[:2]
    x0, y0, x1, y1, z = view_geometry(W, H, region, zoom, max_side)
    cv = cvf.make_canvas(img[y0:y1, x0:x1], x0, y0, z)
    if draw is not None:
        draw(cv)
    cvf.finish(cv, x1 - x0, y1 - y0, 60 if z < 1.5 else 40, grid=(z >= 2) if grid is None else bool(grid))
    return View(frame, x0, y0, x1, y1, z, cv.img)


def _label(cv, text: str, x: float, y: float, color) -> None:
    u, v = cv.to_out(x, y)
    cvf._text(cv.img, text, u + 6, v - 6, color, 0.4)


def draw_marks(cv, marks: list[dict]) -> None:
    """Marks in original px: point [x, y] (open cross-hair), box [x1, y1, x2, y2], line [x1, y1, x2, y2]
    (segment with open cross-hairs at both ends)."""
    for k, m in enumerate(marks):
        col = COLORS[k % len(COLORS)]
        c, kind, lab = m["coords"], m["kind"], str(m.get("label") or "")
        if kind == "point":
            cvf.draw_cross(cv, c[0], c[1], col, arm=12, gap=4)
            if lab:
                _label(cv, lab, c[0], c[1], col)
        elif kind == "box":
            cvf.draw_box(cv, [min(c[0], c[2]), min(c[1], c[3]), max(c[0], c[2]), max(c[1], c[3])], col)
            if lab:
                _label(cv, lab, min(c[0], c[2]), min(c[1], c[3]), col)
        else:
            cvf.draw_segment(cv, c[:2], c[2:], col, stop=6)
            for p in (c[:2], c[2:]):
                cvf.draw_cross(cv, p[0], p[1], col, arm=10, gap=4)
            if lab:
                _label(cv, lab, (c[0] + c[2]) / 2, (c[1] + c[3]) / 2, col)


def _check_marks(marks) -> list[dict]:
    out = []
    for m in marks or []:
        kind, c = m.get("kind"), m.get("coords")
        need = {"point": 2, "box": 4, "line": 4}.get(kind)
        if need is None:
            raise ToolError(f"mark kind must be point, box or line, got {kind!r}")
        if not isinstance(c, list) or len(c) != need or any(_num(v) is None for v in c):
            raise ToolError(f"a {kind} mark needs {need} numbers in coords, got {c!r}")
        out.append({"kind": kind, "coords": [float(v) for v in c], "label": str(m.get("label") or "")})
    return out


# --------------------------------------------------------------------------- tracking

def _match(img: np.ndarray, templ: np.ndarray, centre, radius: float) -> tuple[np.ndarray | None, float]:
    """Best TM_CCOEFF_NORMED match of templ centred within `radius` of `centre` (image index coords:
    pixel (i, j) centred at (j, i)) -> (sub-pixel centre, peak) or (None, -1)."""
    th, tw = templ.shape[:2]
    hx, hy = (tw - 1) / 2, (th - 1) / 2
    x0 = int(math.floor(centre[0] - radius - hx))
    y0 = int(math.floor(centre[1] - radius - hy))
    x1 = int(math.ceil(centre[0] + radius + hx)) + 1
    y1 = int(math.ceil(centre[1] + radius + hy)) + 1
    H, W = img.shape[:2]
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if x1 - x0 < tw + 2 or y1 - y0 < th + 2:
        return None, -1.0
    res = np.nan_to_num(cv2.matchTemplate(img[y0:y1, x0:x1], templ, cv2.TM_CCOEFF_NORMED), nan=-1.0)
    _, peak, _, (j, i) = cv2.minMaxLoc(res)

    def off(a, b, c):
        d = a - 2 * b + c
        return float(np.clip(0.5 * (a - c) / d, -0.5, 0.5)) if d < 0 else 0.0
    dx = off(res[i, j - 1], res[i, j], res[i, j + 1]) if 0 < j < res.shape[1] - 1 else 0.0
    dy = off(res[i - 1, j], res[i, j], res[i + 1, j]) if 0 < i < res.shape[0] - 1 else 0.0
    return np.array([x0 + j + dx + hx, y0 + i + dy + hy]), float(peak)


def ncc_pass(imgs: dict, f_a: int, f_b: int, c_a, tsize: tuple[int, int], guide=None) -> dict:
    """Fallback tracker (same interface as qp.dense_track.track_pass, no scale search): frame-to-frame
    NCC with a constant-velocity search, pulled back onto the anchor template when it still matches.
    {frame: (centre, ncc, 1.0)}; lost frames are absent."""
    step = 1 if f_b >= f_a else -1
    T0 = cv2.getRectSubPix(imgs[f_a], tsize, (float(c_a[0]), float(c_a[1])))
    T = T0
    p, v = np.asarray(c_a, float), np.zeros(2)
    p_last, f_last, lost = p.copy(), f_a, 0
    out = {f_a: (p.copy(), 1.0, 1.0)}
    size = max(tsize)
    for f in range(f_a + step, f_b + step, step):
        img = imgs.get(f)
        if img is None:
            break
        pred = p + v
        radius = max(0.5 * size, 2.0 * float(np.linalg.norm(v)), 4.0) * (1 + 0.5 * lost)
        p1, n1 = _match(img, T, pred, radius)
        if p1 is None or n1 < 0.5:
            lost += 1
            if lost > 8:
                break
            p = pred
            continue
        p2, n2 = _match(img, T0, p1, max(2.0, 0.15 * size))
        if p2 is not None and n2 >= 0.75 and np.linalg.norm(p2 - p1) <= max(1.5, 0.1 * size):
            p1 = p2
        v = (p1 - p_last) / abs(f - f_last)
        p, p_last, f_last, lost = p1, p1.copy(), f, 0
        T = cv2.getRectSubPix(img, tsize, (float(p[0]), float(p[1])))
        out[f] = (p.copy(), n1, 1.0)
    return out


def _box_wh(b) -> tuple[float, float]:
    return float(b[2] - b[0]), float(b[3] - b[1])


def _box_c(b) -> np.ndarray:
    return np.array([(b[0] + b[2]) / 2, (b[1] + b[3]) / 2], float)


def track_object(frames: dict[int, np.ndarray], work_scale: float, size: tuple[int, int],
                 anchors: list[tuple[int, list[float]]], f_lo: int, f_hi: int, fps: float,
                 path_name: str = "", use_dense: bool = True) -> tuple[dict[int, dict], dict]:
    """Per-frame box centre of one object from anchor boxes (original px) over frames f_lo..f_hi.

    frames: {frame: image downscaled by work_scale (work px per original px)}. With qp.dense_track:
    dense_motion between >= 2 anchors (forward/backward fused, chained template offsets), track_pass
    outward from the first / last anchor; otherwise (or when dense_motion fails) single passes from
    each anchor. Every outward pass is checked by a reverse pass from its end (forward-backward error).
    Returns ({frame: {"point", "box", "ncc", "fb"}}, info)."""
    dt = _dense_track() if use_dense else None
    passer = getattr(dt, "track_pass", None) or ncc_pass
    W, H = size
    A = sorted(anchors, key=lambda a: a[0])
    sz = float(np.median([max(_box_wh(b)) for _, b in A]))
    k = min(1.0, TEMPLATE_MAX / max(1.0, sz * work_scale))
    any_img = next(iter(frames.values()))
    ww, wh = any_img.shape[1], any_img.shape[0]
    if k < 1.0:
        size_k = (max(8, round(ww * k)), max(8, round(wh * k)))
        imgs = {f: cv2.resize(im, size_k, interpolation=cv2.INTER_AREA) for f, im in frames.items()}
    else:
        imgs = frames
    iw, ih = next(iter(imgs.values())).shape[1], next(iter(imgs.values())).shape[0]
    S = np.array([iw / W, ih / H])
    info: dict = {"tracker": "dense_track.track_pass" if passer is not ncc_pass else "ncc_fallback",
                  "template_px": round(sz * S[0], 1), "anchors": [a[0] for a in A]}

    def run(fa: int, fb: int, centre, wh) -> dict:
        tsize = (_odd(wh[0] * S[0]), _odd(wh[1] * S[1]))
        raw = passer(imgs, fa, fb, np.asarray(centre, float) * S - 0.5, tsize, None)
        return {f: ((np.asarray(c, float) + 0.5) / S, float(n), float(s)) for f, (c, n, s) in raw.items()}

    def fb_check(fwd: dict, fa: int, wh) -> dict[int, float]:
        """Reverse pass from the far end of `fwd` back to fa: per-frame |forward - backward| px."""
        far = max(fwd, key=lambda f: abs(f - fa))
        if far == fa:
            return {}
        c, _, s = fwd[far]
        rev = run(far, fa, c, (wh[0] * s, wh[1] * s))
        return {f: float(np.linalg.norm(rev[f][0] - fwd[f][0])) for f in fwd if f in rev}

    path: dict[int, dict] = {}
    fb_all: dict[int, float] = {}

    def put(f, centre, wh, ncc=None, fb=None, overwrite=False):
        if f in path and not overwrite:
            return
        x, y = float(centre[0]), float(centre[1])
        path[f] = {"point": [round(x, 2), round(y, 2)],
                   "box": [round(x - wh[0] / 2, 2), round(y - wh[1] / 2, 2), round(x + wh[0] / 2, 2), round(y + wh[1] / 2, 2)],
                   "ncc": None if ncc is None else round(ncc, 3), "fb": None if fb is None else round(fb, 3)}

    def interp_wh(f):
        fr = [a[0] for a in A]
        return (float(np.interp(f, fr, [_box_wh(a[1])[0] for a in A])),
                float(np.interp(f, fr, [_box_wh(a[1])[1] for a in A])))

    # between anchors
    if len(A) >= 2:
        dense = None
        if dt is not None and hasattr(dt, "dense_motion") and hasattr(dt, "Window"):
            try:
                from .spec import Obs
                win = dt.Window(path_name, (W, H), work={f: frames[f] for f in range(A[0][0], A[-1][0] + 1) if f in frames})
                obs = [Obs(t=f / fps, box=list(map(float, b))) for f, b in A]
                dense, dinfo = dt.dense_motion(win, obs, fps)
                info["dense_motion"] = {k2: dinfo.get(k2) for k2 in ("why", "cover", "resid_med", "resid_max", "n_pieces")}
            except Exception as e:  # noqa: BLE001 - fall back to chained passes
                info["dense_motion"] = {"why": f"error:{type(e).__name__}"}
                dense = None
        if dense:
            for f, p in dense.items():
                put(int(f), p, interp_wh(int(f)))
            info["between_anchors"] = "dense_motion"
        else:
            info["between_anchors"] = "chained_passes"
            checks = []
            for (fa, ba), (fb_, bb) in zip(A, A[1:]):
                fwd = run(fa, fb_, _box_c(ba), _box_wh(ba))
                for f, (c, n, s) in fwd.items():
                    if f < fb_:
                        put(f, c, (_box_wh(ba)[0] * s, _box_wh(ba)[1] * s), n)
                if fb_ in fwd:
                    checks.append(round(float(np.linalg.norm(fwd[fb_][0] - _box_c(bb))), 2))
                else:
                    checks.append(None)
            put(A[-1][0], _box_c(A[-1][1]), _box_wh(A[-1][1]), 1.0)
            info["anchor_check_px"] = checks
    # outward from the end anchors (both directions for a single anchor), continuing the path where the
    # between-anchor fusion put the anchor (not at its raw box centre: no step at the anchor frame)
    for (fa, ba), lim in ((A[0], f_lo), (A[-1], f_hi)):
        if lim == fa:
            put(fa, _box_c(ba), _box_wh(ba), 1.0)
            continue
        shift = np.asarray(path[fa]["point"]) - _box_c(ba) if fa in path else np.zeros(2)
        fwd = run(fa, lim, _box_c(ba), _box_wh(ba))
        fb = fb_check(fwd, fa, _box_wh(ba))
        fb_all.update({f: e for f, e in fb.items() if f != fa})
        for f, (c, n, s) in fwd.items():
            put(f, c + shift, (_box_wh(ba)[0] * s, _box_wh(ba)[1] * s), n, fb.get(f))
    path = dict(sorted(path.items()))
    lost = [f for f in range(f_lo, f_hi + 1) if f not in path]
    nccs = [p["ncc"] for p in path.values() if p["ncc"] is not None]
    fbs = list(fb_all.values())
    info.update(n_tracked=len(path), n_frames=f_hi - f_lo + 1, lost=lost,
                ncc_min=_r(min(nccs), 3) if nccs else None, ncc_median=_r(np.median(nccs), 3) if nccs else None,
                fb_median_px=_r(np.median(fbs), 3) if fbs else None, fb_max_px=_r(max(fbs), 3) if fbs else None)
    return path, info


# --------------------------------------------------------------------------- segmentation

def grabcut_measure(img: np.ndarray, box, mode: str, name: str = "") -> dict:
    """GrabCut inside `box` (original px) on one full-resolution frame -> {"extent", "length" (along the
    qp.open.cv_track extent `mode`), "axes" ({measure: {extent, length}} for every MEASURES entry),
    "mask_box", "contours" (original px), "fill", "touch", "rect_long", "rect_short", "angle_deg", "area_px"};
    raises ToolError when the segmentation is empty."""
    from .open.cv_track import extent_from_features, mask_features

    H, W = img.shape[:2]
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    m = 0.25 * max(bw, bh) + 6
    cx0, cy0 = max(0, int(math.floor(x0 - m))), max(0, int(math.floor(y0 - m)))
    cx1, cy1 = min(W, int(math.ceil(x1 + m))), min(H, int(math.ceil(y1 + m)))
    crop = img[cy0:cy1, cx0:cx1]
    ch, cw = crop.shape[:2]
    k = float(np.clip(GC_MIN_SIDE / max(ch, cw), 1.0, 4.0)) if max(ch, cw) < GC_MIN_SIDE else min(1.0, GC_MAX_SIDE / max(ch, cw))
    work = crop if k == 1.0 else cv2.resize(crop, (max(1, round(cw * k)), max(1, round(ch * k))),
                                            interpolation=cv2.INTER_CUBIC if k > 1 else cv2.INTER_AREA)
    kx, ky = work.shape[1] / cw, work.shape[0] / ch
    px, py = GC_RECT_PAD * bw + 1, GC_RECT_PAD * bh + 1
    rx0 = max(1, int(math.floor((x0 - px - cx0) * kx)))
    ry0 = max(1, int(math.floor((y0 - py - cy0) * ky)))
    rx1 = min(work.shape[1] - 1, int(math.ceil((x1 + px - cx0) * kx)))
    ry1 = min(work.shape[0] - 1, int(math.ceil((y1 + py - cy0) * ky)))
    if rx1 - rx0 < 4 or ry1 - ry0 < 4:
        raise ToolError("box too small to segment")
    mask = np.zeros(work.shape[:2], np.uint8)
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.setRNGSeed(0)   # GrabCut initialises its colour models with k-means: deterministic results
    cv2.grabCut(work, mask, (rx0, ry0, rx1 - rx0, ry1 - ry0), bgd, fgd, 5, cv2.GC_INIT_WITH_RECT)
    fg = (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD)
    f = mask_features(fg)
    if f is None:
        raise ToolError("segmentation found no object in the box; give a tighter box or use method 'edges'")
    to_o = lambda p: [round(cx0 + p[0] / kx, 2), round(cy0 + p[1] / ky, 2)]  # noqa: E731
    axes = {}
    for meas, m_ in MEASURES.items():
        ex = extent_from_features(f, m_, name)
        ex = [to_o(ex[0]), to_o(ex[1])]
        axes[meas] = {"extent": ex, "length": round(math.hypot(ex[1][0] - ex[0][0], ex[1][1] - ex[0][1]), 2)}
    ext = extent_from_features(f, mode, name)
    e = [to_o(ext[0]), to_o(ext[1])]
    bx0, by0, bx1, by1 = f["box"]
    cs, _ = cv2.findContours(fg.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [[[cx0 + (q[0] + 0.5) / kx, cy0 + (q[1] + 0.5) / ky] for q in c.reshape(-1, 2)] for c in cs
                if len(c) >= 3]
    rect = f["rect"]
    return {"extent": e, "length": round(math.hypot(e[1][0] - e[0][0], e[1][1] - e[0][1]), 2),
            "mask_box": [round(cx0 + bx0 / kx, 2), round(cy0 + by0 / ky, 2), round(cx0 + bx1 / kx, 2), round(cy0 + by1 / ky, 2)],
            "contours": contours, "fill": round(f["area"] / float((rx1 - rx0) * (ry1 - ry0)), 3),
            "touch": int(sum([bx0 <= rx0, by0 <= ry0, bx1 >= rx1, by1 >= ry1])),
            "rect_long": round(rect[2] / kx, 2), "rect_short": round(rect[3] / kx, 2),
            "angle_deg": round(math.degrees(rect[4]), 1), "area_px": round(f["area"] / (kx * ky), 1),
            "work_scale": round(kx, 3), "axes": axes}


def snap_endpoints(img: np.ndarray, ext, search: float | None = None) -> tuple[list | None, dict]:
    """qp.dense_track.snap_extent on a crop around `ext` (original px): each endpoint moves along the
    extent's line to the strongest edge within +-search px (default max(2, 8% of the length)); ends
    without a clear edge stay ("weak"). (None, info) when snapping is unavailable or fails."""
    dt = _dense_track()
    if dt is None or not hasattr(dt, "snap_extent"):
        return None, {"why": "unavailable"}
    H, W = img.shape[:2]
    e = [[float(v) for v in q] for q in ext]
    L = math.hypot(e[1][0] - e[0][0], e[1][1] - e[0][1])
    search = search or max(2.0, 0.08 * L)
    m = search + 8
    cx0, cy0 = int(max(0, math.floor(min(e[0][0], e[1][0]) - m))), int(max(0, math.floor(min(e[0][1], e[1][1]) - m)))
    cx1, cy1 = int(min(W, math.ceil(max(e[0][0], e[1][0]) + m))), int(min(H, math.ceil(max(e[0][1], e[1][1]) + m)))
    try:
        out, info = dt.snap_extent(img[cy0:cy1, cx0:cx1], [[q[0] - cx0, q[1] - cy0] for q in e], search)
    except Exception as ex:  # noqa: BLE001
        return None, {"why": f"error:{type(ex).__name__}"}
    if out is None:
        return None, info
    return [[round(q[0] + cx0, 2), round(q[1] + cy0, 2)] for q in out], {**info, "search": round(search, 2)}


def _len(e) -> float:
    return math.hypot(e[1][0] - e[0][0], e[1][1] - e[0][1])


SNAP_MAX_CHANGE = 0.15    # a GrabCut extent is replaced by its edge-snapped version only within this change
REFINE_SEARCH = 0.04      # GrabCut refinement: each mask endpoint may move this share of the length ...
REFINE_SEARCH_PX = (2.5, 4.0)   # ... clipped to this many px (colour bleeding is 1-2 px; a wider search
                                # jumps to inner edges of non-convex objects such as lettering)


# --------------------------------------------------------------------------- tool schemas

MEASURES = {"long": "major", "short": "minor", "horizontal": "horizontal", "vertical": "vertical",
            "diameter": "diameter"}   # segment's measure -> qp.open.cv_track extent mode

_STR = {"type": "string"}
_NUM_T = {"type": "number"}
_NUMS = {"type": "array", "items": _NUM_T}
_SPEC = {
    "type": "object",
    "properties": {"target": ca._QUANTITY, "prior": ca._QUANTITY, "notes": _STR},
    "required": ["target", "prior", "notes"],
    "additionalProperties": False,
}
_TRACK = {
    "type": "object",
    "properties": {
        "role": {"type": "string", "enum": list(ROLES)},
        "object": _STR,
        "depth_name": _STR,
        "range_m": {"anyOf": [_NUM_T, {"type": "null"}]},
        "refs": {"type": "array", "items": _STR},
        "obs": {"type": "array", "items": ca._OBS},
    },
    "required": ["role", "object", "depth_name", "range_m", "refs", "obs"],
    "additionalProperties": False,
}
_MARK = {
    "type": "object",
    "properties": {"kind": {"type": "string", "enum": ["point", "box", "line"]}, "coords": _NUMS, "label": _STR},
    "required": ["kind", "coords", "label"],
    "additionalProperties": False,
}

TOOL_DEFS = {
    "get_frames": {
        "description": (
            "Render video frames as images, with tick labels in ORIGINAL pixel coordinates on the margins; "
            "the text before each image gives its frame, time, region, zoom and the exact pixel mapping. "
            "Call it to look at the scene, find the frames and objects you need, and to read positions "
            "precisely: give a region (original px) and a zoom (up to 8) to see edges and endpoints at "
            "sub-pixel level. Draw candidate points, boxes and segments (marks, original px) or stored "
            "measurements (show: T/S ids) on the images to check them before you rely on them. Frames by "
            "index and/or by time (seconds); at most 8 per call. Without region, full frames are shown "
            "downscaled to 1024 px; with a region and no zoom, the largest zoom that fits 1024 px."),
        "input_schema": {
            "type": "object",
            "properties": {
                "frames": {"type": "array", "items": {"type": "integer"}},
                "times": _NUMS,
                "region": _NUMS,
                "zoom": _NUM_T,
                "grid": {"type": "boolean"},
                "marks": {"type": "array", "items": _MARK},
                "show": {"type": "array", "items": _STR},
            },
            "additionalProperties": False,
        },
    },
    "segment": {
        "description": (
            "Measure the extent of one object on one frame and store it as S1, S2, ... Call it for every size "
            "(prior or target), on 2-4 frames where the object is sharp, unoccluded and least foreshortened. "
            "method 'grabcut' (default): give a tight box; the object is segmented inside it and the extent is "
            "read from the mask along `measure`: long (the mask's longest axis, any orientation), short (its "
            "short axis), horizontal / vertical (image x / y extent through the centroid), diameter (round "
            "objects). Choose the measure that matches the asked physical dimension in THIS view (e.g. a car's "
            "width seen from above is its short axis). The mask's endpoints are then moved to the strongest "
            "image edges along the extent (colour bleeding in video makes masks 1-2 px too large; refine false "
            "keeps the raw mask extent). method 'edges': give approximate endpoints as extent "
            "[[x1, y1], [x2, y2]]; each endpoint moves to the strongest edge along the line (on a painted "
            "line or a thin part this may be either of its two edges: check). Returns the endpoints, the "
            "length in px, the mask's other axes and an overlay: check that the mask covers exactly the object "
            "(no shadow, background, reflection or neighbour) and the endpoints sit on its physical ends; if "
            "not, retry with a better box, use 'edges', or place the endpoints yourself in a track's obs."),
        "input_schema": {
            "type": "object",
            "properties": {
                "object": _STR,
                "frame": {"type": "integer"},
                "measure": {"type": "string", "enum": list(MEASURES)},
                "method": {"type": "string", "enum": ["grabcut", "edges"]},
                "refine": {"type": "boolean"},
                "box": _NUMS,
                "extent": {"type": "array", "items": _NUMS},
            },
            "required": ["object", "frame", "measure"],
            "additionalProperties": False,
        },
    },
    "solve": {
        "description": (
            "Compute one question's answer with the geometry program from a spec and tracks (same format as "
            "submit) and return it with its intermediate numbers: the prior as measured in px (or px/s, "
            "px/s^2), metres per pixel, the target in px, in 3D the focal length and ranges, and flags. Call "
            "it for every question before submitting, compare with your own estimate, and fix the spec or "
            "the measurements when they disagree."),
        "input_schema": {
            "type": "object",
            "properties": {"qid": {"type": "integer"}, "spec": _SPEC, "tracks": {"type": "array", "items": _TRACK}},
            "required": ["qid", "spec", "tracks"],
            "additionalProperties": False,
        },
    },
    "submit": {
        "description": (
            "Submit final answers and end the session once every question has one. Per question: "
            "use_last_solve true takes the spec and tracks of that question's latest solve call (else give "
            "spec and tracks), plus direct_answer (your own best estimate in the asked unit, a positive "
            "number), confidence (0-1 that it is within 10%) and a short derivation (<= 200 characters). "
            "Several submit calls are fine; later answers for a qid replace earlier ones."),
        "input_schema": {
            "type": "object",
            "properties": {"answers": {"type": "array", "items": {
                "type": "object",
                "properties": {
                    "qid": {"type": "integer"},
                    "use_last_solve": {"type": "boolean"},
                    "spec": _SPEC,
                    "tracks": {"type": "array", "items": _TRACK},
                    "direct_answer": _NUM_T,
                    "confidence": _NUM_T,
                    "derivation": _STR,
                },
                "required": ["qid", "use_last_solve", "direct_answer", "confidence", "derivation"],
                "additionalProperties": False,
            }}},
            "required": ["answers"],
            "additionalProperties": False,
        },
    },
    "track": {
        "description": (
            "Track one object over time (sub-pixel template matching with drift correction) and store its "
            "box centre and box on every frame as T1, T2, ... Call it for every motion measurement (speed, "
            "acceleration, displacement, path length) and for positions over time. anchors: a tight box "
            "[x1, y1, x2, y2] (original px) around the object on a frame where it is sharp and unoccluded; "
            "add 1-2 more anchors on frames far apart when the motion is long, or the object turns, deforms or "
            "changes size. from_t / to_t (seconds) limit the tracked range (default: the whole clip). Returns "
            "a trajectory table, quality numbers (match score, forward-backward error, lost frames) and images "
            "of the track: check that the box stays on the same object in every shown frame. Put the id in a "
            "track's refs; its points are the box centres."),
        "input_schema": {
            "type": "object",
            "properties": {
                "object": _STR,
                "anchors": {"type": "array", "items": {
                    "type": "object", "properties": {"frame": {"type": "integer"}, "box": _NUMS},
                    "required": ["frame", "box"], "additionalProperties": False}},
                "from_t": _NUM_T,
                "to_t": _NUM_T,
                "overlay": {"type": "boolean"},
            },
            "required": ["object", "anchors"],
            "additionalProperties": False,
        },
    },
}


# Strict schemas compile into a grammar with limits per request (live 400: "limit: 16 parameters with
# unions"); solve / submit carry the nullable spec / track fields (20 union parameters), so only the simple
# tools are strict and solve / submit inputs are validated here (bad input -> an is_error tool_result).
STRICT_TOOLS = ("get_frames", "segment", "track")


def tool_definitions(strict: bool = True) -> list[dict]:
    """Client tools, sorted by name (a fixed, byte-identical tools prefix for the prompt cache)."""
    out = []
    for name in sorted(TOOL_DEFS):
        d = {"name": name, **copy.deepcopy(TOOL_DEFS[name])}
        if strict and name in STRICT_TOOLS:
            d["strict"] = True
        out.append(d)
    return out


# --------------------------------------------------------------------------- system prompt

SYSTEM = """\
You are a measurement agent for QuantiPhy, a benchmark of quantitative physical reasoning from video. \
For ONE video you answer every question by measuring pixels with tools; a geometry program turns your \
measurements into the answers. Answers score only when they are within a few percent of the truth, so \
pixel precision decides everything: an endpoint 2 px off on a 40 px object is already a 5% error.

Task
Each question states one known quantity (the prior), may give object-to-camera distances (depth info, \
3D videos only) and asks for another quantity (the target) in a stated unit. Every answer is (metric \
scale from the prior) x (a pixel measurement of the target). Measure on the frames and use the prior for \
scale; never answer from world knowledge of typical sizes or speeds: many videos are simulations or staged \
scenes with unusual scales, and the prior is exactly true for this video even when it looks implausible. \
2D videos: the motion happens roughly in a plane facing the camera, so one metres-per-pixel scale applies \
to the whole scene. 3D videos: pinhole camera; the scale at an object is proportional to its camera \
distance (metres per pixel = range / focal length in px); the depth info gives ranges of listed objects at \
stated times and the program fits the focal length to the prior (or uses the camera's when the first \
message states it).

Coordinates
- Every coordinate you give or receive is in ORIGINAL video pixels (size in the first message), continuous: \
x to the right, y down, origin at the top-left corner; the pixel in column j spans x = j..j+1.
- Frame f is at time t = f / fps; frames are 0..N-1.
- Pixel motion is relative to the camera. If the camera pans or zooms (check a static background feature, \
e.g. track it), say so in notes and base your direct answer on motion relative to the static scene.
- Every image has dark margins with tick labels in original pixels. The text before each image gives its \
frame, the region shown and the zoom with the exact mapping from the image's own pixels (u, v) to original \
pixels. Read positions from the ticks or with that mapping; never report image pixels.

Tools and how to use them
- get_frames: overview frames, and zoomed crops (region + zoom) for precise points, edges and endpoints. \
Before relying on a manual point, box or endpoint, draw it with marks on a zoomed crop and correct it \
until it sits exactly where it should. Several frames per call and several calls per response are fine.
- track: for anything that moves. Give a tight box on a clear frame (add anchors on frames far apart for \
long or changing motion); check the quality numbers and the images: the box must stay on the same object \
in every frame. A low match score, a large forward-backward error or lost frames mean the track drifted: \
re-anchor, shorten the range or measure by hand.
- segment: for sizes. Check the overlay: the mask must be exactly the object. Measure on 2-4 frames and \
compare the lengths: they should agree within a few percent unless the object turns or deforms.
- solve: runs the geometry program on one question. Use it on every question; read the intermediate \
numbers (prior px, metres per px, target px) and check them against your own understanding.
- submit: final answers. The session ends when every question has an answer.
Batch independent calls (several get_frames / track / segment calls) in one response to save turns.

Workflow
1. Read all questions; list the objects and measurements each needs. Shared objects (usually the prior) \
are measured once and referenced by every question that needs them.
2. Measure the prior first and best: it scales every answer of the video.
3. Measure each target; solve each question; fix what is inconsistent (wrong object instance, wrong \
dimension, a drifting track, a mask that includes a shadow).
4. Submit all answers, with your own direct answer per question.

Spec (solve and submit): {target, prior, notes}; target and prior each have
- kind: size (extent of one object: length, height, width, diameter, wingspan, thickness ...), distance \
(between two objects or two points at one time; between an object and a surface or line - floor, ground, \
water, table top, wall, court line - with objects [object, surface]), displacement (straight-line \
distance an object moves between two times), path_length (distance travelled along the path), speed \
(magnitude of velocity at a time, or averaged over a window), acceleration, camera_distance \
(object-to-camera distance, from the depth info), other.
- objects: short noun phrases, e.g. ["bird"]; two entries for a distance.
- dimension: for a size the measured dimension ("length", "height", "width", "diameter", "wingspan" ...); \
otherwise "".
- time: the instant in seconds ("at 1.5s", "t=1.5"); "final"/"at the end" -> the time of the last \
frame; "initial"/"at the start" -> 0; null if not time-specific or when a window applies.
- window: [t0, t1] for a time range: "from A to B" / "between A and B" -> [A, B]; "before T" -> [0, T]; \
"after T" -> [T, time of the last frame]; "in the first T seconds" -> [0, T]; null otherwise (time and \
window both null = the whole clip).
- axis: "horizontal" or "vertical" when the question or prior says so (a gravity prior is vertical); \
otherwise "any".
- value_si: prior only, the known value in SI (m, m/s, m/s^2): 57.2mm -> 0.0572; null for the target.
- unit: target only, the asked unit ("m", "cm", "mm", "m/s", "cm/s", "m/s^2", "cm/s^2" ...); "" for the \
prior.
- notes: ambiguities or typos in the question; "" if none. (The program reads the depth info text itself.)

Tracks (solve and submit): one per role
- role: "prior" (the object carrying the known quantity), "target" (the object asked about), "target2" \
(the second object or the surface of a distance), "prior2" (the second object when the prior is a \
distance). When prior and target are the same object still give both tracks (e.g. the prior's motion, the \
target's extents), referencing the same measurements where they apply.
- object: its name. depth_name (3D): the object name exactly as written in the depth info whose distance \
is this object's (e.g. "distance_red_crate_camera" -> "red_crate"), also when the question calls it \
differently; "" when none applies and in 2D. range_m (3D, only when depth_name is ""): your estimate of \
the object's camera distance in metres at the measured frames (from objects with known distance it \
stands next to, or from its apparent size); else null.
- refs: ids of stored measurements (T1, S2 ...) this track uses; obs: manual observations {frame, point \
[x, y], extent [[x1, y1], [x2, y2]], box [x1, y1, x2, y2]} with null for fields you do not give. refs and \
obs are combined.
What the program reads from a track
- size: the extent endpoints (else the box sides), median over the observations (or those within 0.5 s \
of the asked time). Extent = the two physical ends of exactly the asked dimension. Height = a vertical \
physical line from the object's top to the point on its supporting surface directly below (in an \
elevated or oblique view the image-vertical extent of a car or box also contains its top surface: never \
use the box height then). Length or width seen at an angle = the two physical ends along that dimension \
(bumper to bumper), not the box diagonal. Wingspan = wingtip to wingtip; diameter = edge to edge through \
the centre. Avoid motion-blurred frames (blur stretches the object along the motion).
- motion (speed, acceleration, displacement, path length): the points over time (robust local polynomial \
fits). Use the tracker's box centres (never a top, bottom or edge point, which moves when the apparent \
size changes); cover the asked times and window ends. For a gravity prior ("gravity acc = 9.8 m/s^2") the \
prior object is the one in free fall or projectile flight: track it only while in flight (axis \
"vertical").
- distance: points of both tracks (target and target2) on the SAME frames at the asked time: centres \
unless the question implies edges or a gap ("minimum", "closest", "gap": the nearest points). For an \
object and a surface, target2 is the point on the surface directly below the object (perpendicular for \
walls and lines).
- 3D: give boxes on the frames at the depth-info times (apparent size tells how the range changes). A \
size between two parts that the depth info lists separately (ramp_far and ramp_near, shelf_left and \
shelf_right) is kind "distance" with objects named as in the depth info, target and target2 at those \
physical points with depth_name set. camera_distance targets need no observations (set depth_name).
- Same object, several questions: identify the instance carefully (nearest, left, big, the one the \
depth info names) and use the same instance in every question.

Answers (submit): direct_answer = your own best estimate in the asked unit computed from your \
measurements (positive number); confidence = 0-1 that it is within 10%; derivation = the pixel numbers and \
scale you used, at most 200 characters.

Budget: after each tool round a status line gives the turns and budget used. When it says to wrap up, \
submit at once with your best answers for every question."""


# --------------------------------------------------------------------------- measurements and session

@dataclass
class Measurement:
    mid: str                  # "T1", "S2", ...
    kind: str                 # "track" | "segment"
    object: str
    obs: list[dict]           # {"frame", "point", "extent", "box"}, original px
    info: dict = field(default_factory=dict)


@dataclass
class ToolOutput:
    content: list[dict]       # tool_result content blocks (text / image)
    is_error: bool = False
    summary: str = ""


def _text(s: str) -> dict:
    return {"type": "text", "text": s}


def _image(b64: str) -> dict:
    return {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}}


class AgentSession:
    """Tools and state of one video: frames, stored measurements, solve history and submitted answers."""

    def __init__(self, rows: pd.DataFrame, image_dir: str | Path | None = None, use_dense: bool = True):
        self.rows = rows.reset_index(drop=True)
        first = self.rows.iloc[0]
        self.video_id, self.path = str(first.video_id), str(first.video_path)
        self.fps, self.fps_from_container = ca.video_fps(first.fps, self.path)
        self.n_frames, W, H = ca.video_info(self.path)
        self.size = (int(W), int(H))
        self.video_type = str(first.video_type)
        self.is_3d = self.video_type[1:2] == "3"
        self.source = str(getattr(first, "video_source", "") or "")
        self.qids = [int(q) for q in self.rows.qid]
        self.store = FrameStore(self.path, self.n_frames, self.size)
        self.use_dense = use_dense
        self.meas: dict[str, Measurement] = {}
        self._count = Counter()
        self.last_solve: dict[int, dict] = {}
        self.submitted: dict[int, dict] = {}
        self.done = False
        self.image_dir = Path(image_dir) if image_dir else None
        self.saved: dict[str, str] = {}          # sha1 of base64 data -> file name
        self.n_images = 0

    # ----------------------------------------------------------------- basics

    @property
    def W(self) -> int:
        return self.size[0]

    @property
    def H(self) -> int:
        return self.size[1]

    def frame_at(self, t: float) -> int:
        return int(min(max(round(float(t) * self.fps), 0), self.n_frames - 1))

    def camera_fov(self) -> float | None:
        return ca.LAB_FOV_DEG if self.source in combine.CAMERA_SOURCES and self.is_3d else None

    def meta(self) -> dict:
        """Record meta in qp.claude_annotate's format (original px: scale 1, every frame valid)."""
        return {"video_id": self.video_id, "fps": self.fps, "fps_from_container": self.fps_from_container,
                "video_type": self.video_type, "n_frames_total": self.n_frames, "scale": 1.0,
                "image_size": list(self.size), "frames": list(range(self.n_frames)),
                "questions": [{"qid": int(r.qid), "target_unit": r.target_unit, "prior": str(r.prior),
                               "depth_info": str(r.depth_info or "")} for r in self.rows.itertuples()],
                "prompt_version": "v2", "agent_version": AGENT_VERSION, "video_source": self.source}

    def _new_id(self, prefix: str) -> str:
        self._count[prefix] += 1
        return f"{prefix}{self._count[prefix]}"

    def _emit(self, img: np.ndarray, tag: str) -> tuple[dict, int, int]:
        """Image block (+ saved JPEG when image_dir is set) and its size."""
        b64 = _jpeg_b64(img)
        self.n_images += 1
        if self.image_dir is not None:
            self.image_dir.mkdir(parents=True, exist_ok=True)
            name = f"img_{self.n_images:03d}_{tag}.jpg"
            (self.image_dir / name).write_bytes(base64.b64decode(b64))
            self.saved[hashlib.sha1(b64.encode()).hexdigest()[:16]] = name
        return _image(b64), img.shape[1], img.shape[0]

    def _frame_check(self, f) -> int:
        if not isinstance(f, (int, np.integer)) or isinstance(f, bool) or not 0 <= int(f) < self.n_frames:
            raise ToolError(f"frame {f!r} is not in 0..{self.n_frames - 1}")
        return int(f)

    def _box_check(self, b, what: str = "box") -> list[float]:
        if not isinstance(b, list) or len(b) != 4 or any(_num(v) is None for v in b):
            raise ToolError(f"{what} must be [x1, y1, x2, y2] in original pixels")
        x0, x1 = sorted((float(b[0]), float(b[2])))
        y0, y1 = sorted((float(b[1]), float(b[3])))
        x0, y0, x1, y1 = max(0.0, x0), max(0.0, y0), min(float(self.W), x1), min(float(self.H), y1)
        if x1 - x0 < 2 or y1 - y0 < 2:
            raise ToolError(f"{what} {b} is smaller than 2 px or outside the {self.W}x{self.H} image")
        return [x0, y0, x1, y1]

    # ----------------------------------------------------------------- first message

    def overview_frames(self, n: int = OVERVIEW_FRAMES, extra: int = OVERVIEW_EXTRA) -> list[int]:
        last = self.n_frames - 1
        uni = sorted(set(np.linspace(0, last, max(1, min(n, self.n_frames))).round().astype(int).tolist()))
        texts = [t for r in self.rows.itertuples() for t in (r.question, r.prior, r.depth_info)]
        times = [self.frame_at(t) for t in ca.mentioned_times_v2(texts)]
        add = [f for f in dict.fromkeys(times) if f not in uni][:extra]
        return sorted(uni + add)

    def initial_content(self, n_overview: int = OVERVIEW_FRAMES, max_turns: int = MAX_TURNS,
                        max_usd: float = MAX_USD_VIDEO) -> list[dict]:
        first = self.rows.iloc[0]
        frames = self.overview_frames(n_overview)
        imgs = self.store.get(frames)
        dur = self.n_frames / self.fps
        cam = ca._camera_note(first, self.W) if self.is_3d else ""
        head = (f"Video {self.video_id}: {'3D video with camera distances' if self.is_3d else '2D video'}; "
                f"{self.W}x{self.H} px (original pixels); {self.fps:g} fps; {self.n_frames} frames, "
                f"0..{self.n_frames - 1} (~{dur:.2f} s).{cam} {len(imgs)} overview frames follow (full "
                f"frames{' downscaled' if max(self.size) > OVERVIEW_SIDE else ''}; tick labels in original px).")
        content = [_text(head)]
        for f in frames:
            if f not in imgs:
                continue
            v = render_view(imgs[f], f, None, None, OVERVIEW_SIDE, grid=False)
            block, w, h = self._emit(v.img, f"overview_f{f}")
            content += [_text(f"Frame {f} (t={f / self.fps:.3f}s), full frame, zoom {v.zoom:.4g}: {v.mapping()}"),
                        block]
        blocks = "\n\n".join(ca._question_block(r) for r in self.rows.itertuples())
        content.append(_text(
            f"{len(self.rows)} question(s) about this video:\n\n{blocks}\n\n"
            f"Measure and answer all of them (qids {', '.join(map(str, self.qids))}) with the tools, then "
            f"submit. Limits for this video: {max_turns} responses and about ${max_usd:.2f}."))
        return content

    # ----------------------------------------------------------------- dispatch

    def execute(self, name: str, inp: dict) -> ToolOutput:
        fn = {"get_frames": self.get_frames, "track": self.track, "segment": self.segment,
              "solve": self.solve, "submit": self.submit}.get(name)
        if fn is None:
            return ToolOutput([_text(f"unknown tool {name!r}")], True, "unknown tool")
        try:
            return fn(inp if isinstance(inp, dict) else {})
        except ToolError as e:
            return ToolOutput([_text(f"Error: {e}")], True, f"error: {e}")
        except Exception as e:  # noqa: BLE001 - a tool bug must not end the session
            return ToolOutput([_text(f"Internal error in {name}: {type(e).__name__}: {e}")], True,
                              f"internal error {type(e).__name__}")

    # ----------------------------------------------------------------- get_frames

    def get_frames(self, inp: dict) -> ToolOutput:
        frames = [self._frame_check(f) for f in inp.get("frames") or []]
        for t in inp.get("times") or []:
            if _num(t) is None:
                raise ToolError(f"time {t!r} is not a number")
            frames.append(self.frame_at(t))
        frames = list(dict.fromkeys(frames))
        if not frames:
            raise ToolError("give frames (indices) or times (seconds)")
        note = ""
        if len(frames) > MAX_IMAGES:
            note = f" (only the first {MAX_IMAGES} of {len(frames)} frames are shown)"
            frames = frames[:MAX_IMAGES]
        marks = _check_marks(inp.get("marks"))
        show = [str(s) for s in inp.get("show") or []]
        unknown = [s for s in show if s not in self.meas]
        if unknown:
            raise ToolError(f"unknown measurement ids {unknown}; stored: {sorted(self.meas) or 'none'}")
        imgs = self.store.get(frames)
        content, tokens = [], 0
        for f in frames:
            def draw(cv, f=f):
                self._draw_show(cv, show, f)
                draw_marks(cv, marks)
            v = render_view(imgs[f], f, inp.get("region"), inp.get("zoom"), VIEW_SIDE, inp.get("grid"), draw)
            block, w, h = self._emit(v.img, f"view_f{f}")
            tokens += image_tokens(w, h)
            what = "full frame" if (v.x0, v.y0, v.x1, v.y1) == (0, 0, self.W, self.H) else \
                f"region x {v.x0}..{v.x1}, y {v.y0}..{v.y1}"
            content += [_text(f"Frame {f} (t={f / self.fps:.3f}s), {what}, zoom {v.zoom:.4g}: {v.mapping()}"), block]
        if note:
            content.insert(0, _text(note.strip()))
        return ToolOutput(content, False, f"{len(frames)} image(s), ~{tokens} tokens{note}")

    def _draw_show(self, cv, ids: list[str], f: int) -> None:
        for k, mid in enumerate(ids):
            m = self.meas[mid]
            col = COLORS[(k + 3) % len(COLORS)]
            for o in m.obs:
                if o["frame"] != f:
                    continue
                if o.get("box"):
                    cvf.draw_box(cv, o["box"], col)
                if o.get("point"):
                    cvf.draw_cross(cv, o["point"][0], o["point"][1], col, arm=10, gap=3)
                    _label(cv, mid, o["point"][0], o["point"][1], col)
                if o.get("extent"):
                    a, b = o["extent"]
                    cvf.draw_segment(cv, a, b, col, stop=6)
                    for p in (a, b):
                        cvf.draw_cross(cv, p[0], p[1], col, arm=10, gap=4)
                    _label(cv, mid, (a[0] + b[0]) / 2, (a[1] + b[1]) / 2, col)

    # ----------------------------------------------------------------- track

    def track(self, inp: dict) -> ToolOutput:
        name = str(inp.get("object") or "object")
        anchors = []
        for a in inp.get("anchors") or []:
            if not isinstance(a, dict):
                raise ToolError("each anchor is {frame, box}")
            anchors.append((self._frame_check(a.get("frame")), self._box_check(a.get("box"), "anchor box")))
        if not anchors:
            raise ToolError("give at least one anchor {frame, box}")
        anchors = sorted(dict(anchors).items())
        f_lo = 0 if _num(inp.get("from_t")) is None else self.frame_at(inp["from_t"])
        f_hi = self.n_frames - 1 if _num(inp.get("to_t")) is None else self.frame_at(inp["to_t"])
        f_lo, f_hi = min(f_lo, anchors[0][0]), max(f_hi, anchors[-1][0])
        frames, s = self.store.work(f_lo, f_hi)
        if any(f not in frames for f, _ in anchors):
            raise ToolError("could not decode the anchor frames")
        f_hi = min(f_hi, max(frames))
        path, info = track_object(frames, s, self.size, anchors, f_lo, f_hi, self.fps, self.path, self.use_dense)
        del frames
        mid = self._new_id("T")
        obs = [{"frame": f, "point": p["point"], "extent": None, "box": p["box"]} for f, p in path.items()]
        self.meas[mid] = Measurement(mid, "track", name, obs, {**info, "work_scale": round(s, 4)})
        text = self._track_text(mid, name, path, info, f_lo, f_hi)
        content = [_text(text)]
        if inp.get("overlay", True) and len(path) >= 1:
            content += self._track_overlay(mid, path, anchors)
        return ToolOutput(content, False, f"{mid} {name}: {info['n_tracked']}/{info['n_frames']} frames, "
                                          f"fb_max {info['fb_max_px']}, ncc_min {info['ncc_min']}")

    def _track_text(self, mid: str, name: str, path: dict, info: dict, f_lo: int, f_hi: int) -> str:
        fr = sorted(path)
        lines = [f"{mid} \"{name}\": tracked {info['n_tracked']} of {info['n_frames']} frames ({f_lo}..{f_hi}); "
                 f"anchors at frames {info['anchors']}; tracker {info['tracker']} (template {info['template_px']} "
                 f"px at the working scale)."]
        q = [f"match score min {info['ncc_min']} median {info['ncc_median']}" if info["ncc_min"] is not None else "",
             f"forward-backward error median {info['fb_median_px']} px, max {info['fb_max_px']} px"
             if info["fb_max_px"] is not None else ""]
        if info.get("between_anchors"):
            q.append(f"between anchors: {info['between_anchors']}"
                     + (f" {info.get('dense_motion')}" if info.get("dense_motion") else "")
                     + (f", tracked vs next anchor centre {info['anchor_check_px']} px" if info.get("anchor_check_px") else ""))
        lost = info["lost"]
        q.append(f"lost frames: {len(lost)}" + (f" ({lost[:12]}{' ...' if len(lost) > 12 else ''})" if lost else ""))
        lines.append("Quality: " + "; ".join(x for x in q if x) + ".")
        if fr:
            p0, p1 = np.array(path[fr[0]]["point"]), np.array(path[fr[-1]]["point"])
            pts = np.array([path[f]["point"] for f in fr])
            plen = float(np.sum(np.linalg.norm(np.diff(pts, axis=0), axis=1))) if len(pts) > 1 else 0.0
            b0, b1 = path[fr[0]]["box"], path[fr[-1]]["box"]
            lines.append(f"Net displacement frame {fr[0]} -> {fr[-1]}: ({p1[0] - p0[0]:+.2f}, {p1[1] - p0[1]:+.2f}) px, "
                         f"|d| = {np.linalg.norm(p1 - p0):.2f} px; summed path {plen:.2f} px; box "
                         f"{b0[2] - b0[0]:.1f}x{b0[3] - b0[1]:.1f} -> {b1[2] - b1[0]:.1f}x{b1[3] - b1[1]:.1f} px.")
            step = max(1, math.ceil(len(fr) / TRACK_ROWS))
            show = sorted(set(fr[::step]) | {fr[-1]} | {f for f in info["anchors"] if f in path})
            lines.append(f"frame  t(s)    x        y        w      h      score  fb   (every {step} frame(s); all "
                         f"{len(fr)} stored in {mid})")
            for f in show:
                p = path[f]
                b = p["box"]
                lines.append(f"{f:<6d} {f / self.fps:<7.3f} {p['point'][0]:<8.2f} {p['point'][1]:<8.2f} "
                             f"{b[2] - b[0]:<6.1f} {b[3] - b[1]:<6.1f} {'-' if p['ncc'] is None else p['ncc']:<6} "
                             f"{'-' if p['fb'] is None else p['fb']}")
        return "\n".join(lines)

    def _track_overlay(self, mid: str, path: dict, anchors) -> list[dict]:
        fr = sorted(path)
        pts = np.array([path[f]["point"] for f in fr])
        boxes = np.array([path[f]["box"] for f in fr])
        x0, y0 = float(boxes[:, 0].min()), float(boxes[:, 1].min())
        x1, y1 = float(boxes[:, 2].max()), float(boxes[:, 3].max())
        m = 0.15 * max(x1 - x0, y1 - y0) + 16
        ref = anchors[0][0]
        img = self.store.get([ref])[ref]

        def draw(cv):
            col = COLORS[0]
            for a, b in zip(pts, pts[1:]):
                cvf.draw_segment(cv, a, b, col)
            step = max(1, math.ceil(len(fr) / 10))
            for i in range(0, len(fr), step):
                u, v = cv.to_out(*pts[i])
                cv2.circle(cv.img, cvf._pt(u, v), 2 * 16, col, -1, cv2.LINE_AA, 4)
                cvf._text(cv.img, str(fr[i]), u + 4, v - 4, col, 0.35)
            cvf.draw_box(cv, path[fr[0]]["box"], COLORS[2])
            cvf.draw_box(cv, path[fr[-1]]["box"], COLORS[1])
        v = render_view(img, ref, [x0 - m, y0 - m, x1 + m, y1 + m], None, VIEW_SIDE, False, draw)
        if v.zoom > 4:
            v = render_view(img, ref, [x0 - m, y0 - m, x1 + m, y1 + m], 4, VIEW_SIDE, False, draw)
        b1, _, _ = self._emit(v.img, f"{mid}_path")
        out = [_text(f"{mid} trajectory drawn on frame {ref} (red dots labelled with frame numbers; green box = "
                     f"frame {fr[0]}, magenta box = frame {fr[-1]}), region x {v.x0}..{v.x1}, y {v.y0}..{v.y1}, "
                     f"zoom {v.zoom:.4g}: {v.mapping()}"), b1]
        picks = sorted(set(fr[int(round(i))] for i in np.linspace(0, len(fr) - 1, min(4, len(fr)))))
        crops = self.store.get(picks)
        tiles = []
        for f in picks:
            b = path[f]["box"]
            c, s = _box_c(b), max(b[2] - b[0], b[3] - b[1]) * 1.25 + 12
            cx0, cy0 = int(max(0, math.floor(c[0] - s))), int(max(0, math.floor(c[1] - s)))
            cx1, cy1 = int(min(self.W, math.ceil(c[0] + s))), int(min(self.H, math.ceil(c[1] + s)))
            sub = crops[f][cy0:cy1, cx0:cx1].copy()
            if sub.size == 0:
                continue
            k = 200.0 / sub.shape[0]
            sub = cv2.resize(sub, (max(1, round(sub.shape[1] * k)), 200), interpolation=cv2.INTER_CUBIC)
            canvas = cvf.Canvas(sub, cx0, cy0, k, 0, 0)
            cvf.draw_box(canvas, b, COLORS[2])
            cvf.draw_cross(canvas, path[f]["point"][0], path[f]["point"][1], COLORS[2], arm=8, gap=3)
            cvf._text(sub, f"f{f}", 4, 16, (255, 255, 255), 0.45)
            tiles += [sub, np.full((200, 4, 3), 32, np.uint8)]
        if tiles:
            strip = np.hstack(tiles[:-1])
            if strip.shape[1] > VIEW_SIDE:
                k = VIEW_SIDE / strip.shape[1]
                strip = cv2.resize(strip, (VIEW_SIDE, max(1, round(strip.shape[0] * k))), interpolation=cv2.INTER_AREA)
            b2, _, _ = self._emit(strip, f"{mid}_strip")
            out += [_text(f"{mid} on frames {picks}: the tracked box and centre on each frame (no ticks)."), b2]
        return out

    # ----------------------------------------------------------------- segment

    def segment(self, inp: dict) -> ToolOutput:
        f = self._frame_check(inp.get("frame"))
        name = str(inp.get("object") or "object")
        measure = inp.get("measure") or "long"
        if measure not in MEASURES:
            raise ToolError(f"measure must be one of {list(MEASURES)}")
        method = inp.get("method") or ("edges" if inp.get("extent") and not inp.get("box") else "grabcut")
        img = self.store.get([f])[f]
        notes = []
        if method == "grabcut":
            box = self._box_check(inp.get("box"))
            r = grabcut_measure(img, box, MEASURES[measure], name)
            ext = r["extent"]
            snapped, sinfo = (snap_endpoints(img, ext, float(np.clip(REFINE_SEARCH * r["length"], *REFINE_SEARCH_PX)))
                              if inp.get("refine", True) and r["length"] >= 3 else (None, {"why": "off"}))
            ends = [sinfo.get("end0"), sinfo.get("end1")]
            refined = (snapped is not None and all(isinstance(x, (int, float)) for x in ends)
                       and abs(_len(snapped) / max(r["length"], 1e-9) - 1) <= SNAP_MAX_CHANGE)
            mask_ext = ext
            if refined:
                ext = snapped
            obs = {"frame": f, "point": None, "extent": ext, "box": r["mask_box"]}
            warn = []
            if not GC_FILL[0] <= r["fill"] <= GC_FILL[1]:
                warn.append(f"mask fills {r['fill']:.0%} of the seed box (suspicious)")
            if r["touch"] >= 3:
                warn.append(f"mask touches {r['touch']} sides of the seed box (it may leak into the background)")
            others = ", ".join(f"{k} {v['length']:.2f}" for k, v in r["axes"].items() if k != measure)
            how = (f"edge-refined mask extent (endpoints moved {ends[0]:+.2f} / {ends[1]:+.2f} px along the line to the "
                   f"strongest edges; mask extent {r['length']:.2f} px)" if refined else
                   f"mask extent (edge refinement not applied: {sinfo.get('why') if snapped is None else ends})")
            text = (f"grabcut, measure {measure}: extent ({ext[0][0]:.2f}, {ext[0][1]:.2f}) - "
                    f"({ext[1][0]:.2f}, {ext[1][1]:.2f}), length {_len(ext):.2f} px [{how}]. Other axes of the mask (px): "
                    f"{others}. Mask box {r['mask_box']} ({r['mask_box'][2] - r['mask_box'][0]:.1f} x "
                    f"{r['mask_box'][3] - r['mask_box'][1]:.1f} px), area {r['area_px']} px^2, long axis at "
                    f"{r['angle_deg']} deg, fill {r['fill']} of your box.")
            if warn:
                text += " Warning: " + "; ".join(warn) + "."
            contours = r["contours"]
            region_box = box
        elif method == "edges":
            e = inp.get("extent")
            if not (isinstance(e, list) and len(e) == 2 and all(isinstance(q, list) and len(q) == 2 and
                                                               all(_num(v) is not None for v in q) for q in e)):
                raise ToolError("method 'edges' needs extent [[x1, y1], [x2, y2]] in original pixels")
            e = [[float(v) for v in q] for q in e]
            L = _len(e)
            if L < 3:
                raise ToolError("extent shorter than 3 px")
            ext, sinfo = snap_endpoints(img, e, max(3.0, 0.08 * L))
            if ext is None:
                raise ToolError(f"edge snapping failed ({sinfo.get('why')}); place the endpoints by hand")
            moved = [sinfo.get("end0"), sinfo.get("end1")]
            box = self._box_check(inp["box"]) if inp.get("box") else None
            obs = {"frame": f, "point": None, "extent": ext, "box": box}
            text = (f"edges: extent ({ext[0][0]:.2f}, {ext[0][1]:.2f}) - ({ext[1][0]:.2f}, {ext[1][1]:.2f}), length "
                    f"{_len(ext):.2f} px (given {L:.2f} px; endpoint shifts along the line {moved}, 'weak' = no clear "
                    f"edge, kept).")
            contours, mask_ext = [], None
            region_box = [min(q[0] for q in ext + e), min(q[1] for q in ext + e),
                          max(q[0] for q in ext + e), max(q[1] for q in ext + e)]
        else:
            raise ToolError("method must be 'grabcut' or 'edges'")
        mid = self._new_id("S")
        self.meas[mid] = Measurement(mid, "segment", name, [obs], {"method": method, "measure": measure})
        text = f"{mid} \"{name}\" frame {f} (t={f / self.fps:.3f}s): " + text + (f" ({'; '.join(notes)})" if notes else "")

        def draw(cv):
            for c in contours:
                pts = np.array([cv.to_out(x, y) for x, y in c], np.float64)
                cv2.polylines(cv.img, [np.round((pts - 0.5) * 16).astype(np.int32)], True, (0, 200, 0), 1,
                              cv2.LINE_AA, 4)
            if method == "grabcut":
                cvf.draw_box(cv, region_box, (0, 255, 255))
            if mask_ext is not None and mask_ext != ext:
                for q in mask_ext:
                    cvf.draw_cross(cv, q[0], q[1], (0, 200, 0), arm=8, gap=3)
            a, b = ext
            cvf.draw_segment(cv, a, b, (255, 0, 255), stop=7)
            for p in (a, b):
                cvf.draw_cross(cv, p[0], p[1], (255, 0, 255), arm=12, gap=4)
            _label(cv, mid, (a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (255, 0, 255))
        bw, bh = region_box[2] - region_box[0], region_box[3] - region_box[1]
        m = 0.3 * max(bw, bh) + 8
        v = render_view(img, f, [region_box[0] - m, region_box[1] - m, region_box[2] + m, region_box[3] + m],
                        None, VIEW_SIDE, None, draw)
        block, _, _ = self._emit(v.img, f"{mid}_f{f}")
        legend = ("green = mask outline (green crosses: the mask's own endpoints), yellow = your box, "
                  if method == "grabcut" else "")
        content = [_text(text), _text(f"{mid} overlay ({legend}magenta = measured extent), frame {f}, region x "
                                      f"{v.x0}..{v.x1}, y {v.y0}..{v.y1}, zoom {v.zoom:.4g}: {v.mapping()}"), block]
        return ToolOutput(content, False, f"{mid} {name} {method}: {text.split(': ', 1)[-1][:120]}")

    # ----------------------------------------------------------------- solve / submit

    def resolve_tracks(self, tracks) -> list[dict]:
        """Tracks in claude_annotate's parsed format with refs expanded into obs (copies)."""
        out = []
        if not isinstance(tracks, list):
            raise ToolError("tracks must be a list")
        for tr in tracks:
            if not isinstance(tr, dict) or tr.get("role") not in ROLES:
                raise ToolError(f"each track needs a role in {list(ROLES)}")
            obs = []
            for mid in tr.get("refs") or []:
                if mid not in self.meas:
                    raise ToolError(f"unknown measurement id {mid!r}; stored: {sorted(self.meas) or 'none'}")
                obs += copy.deepcopy(self.meas[mid].obs)
            for o in tr.get("obs") or []:
                if not isinstance(o, dict):
                    raise ToolError("each obs is {frame, point, extent, box}")
                self._frame_check(o.get("frame"))
                obs.append({"frame": int(o["frame"]), "point": o.get("point"), "extent": o.get("extent"),
                            "box": o.get("box")})
            out.append({"role": tr["role"], "object": str(tr.get("object") or ""),
                        "depth_name": str(tr.get("depth_name") or ""), "range_m": _num(tr.get("range_m")),
                        "refs": list(tr.get("refs") or []), "obs": obs})
        return out

    def _question(self, qid: int, spec: dict, tracks: list[dict], direct=None, confidence=None,
                  derivation: str = "") -> dict:
        if not isinstance(spec, dict) or "target" not in spec or "prior" not in spec:
            raise ToolError("spec needs target and prior")
        return {"qid": int(qid), "spec": {"target": spec["target"], "prior": spec["prior"], "depth": [],
                                          "notes": str(spec.get("notes") or "")},
                "tracks": tracks, "direct_answer": direct, "confidence": confidence, "derivation": derivation}

    def _qid(self, q) -> int:
        if not isinstance(q, (int, np.integer)) or int(q) not in self.qids:
            raise ToolError(f"qid {q!r} is not one of {self.qids}")
        return int(q)

    def geometry(self, question: dict):
        """(Annotation, geometry Answer) of one parsed question (pass-1 normalisation + qp.geometry.solve)."""
        from .geometry import solve as geo_solve

        anns = ca.to_annotations({"questions": [question]}, self.meta(), source="agent")
        a = anns.get(int(question["qid"]))
        if a is None:
            raise ToolError("the question could not be parsed")
        fov = self.camera_fov()
        ans = geo_solve(a.spec, a.tracks, self.size, self.fps, **({"camera_fov_deg": fov} if fov else {}))
        return a, ans

    def solve(self, inp: dict) -> ToolOutput:
        qid = self._qid(inp.get("qid"))
        q = self._question(qid, inp.get("spec"), self.resolve_tracks(inp.get("tracks") or []))
        a, ans = self.geometry(q)
        self.last_solve[qid] = q
        text = self._solve_text(qid, a, ans)
        return ToolOutput([_text(text)], False, text.split("\n")[0][:160])

    def _solve_text(self, qid: int, a, ans) -> str:
        unit = a.spec.target.unit or "SI"
        head = (f"qid {qid}: geometry answer {_fmt(ans.value)} {unit} (method {ans.method or '-'})"
                if ans.value is not None else f"qid {qid}: geometry could not solve it (flags: {', '.join(ans.flags)})")
        lines = [head]
        p, t = a.spec.prior, a.spec.target
        lines.append(f"prior used: {p.kind} {p.dimension} of {p.objects} = {_fmt(p.value_si)} SI (from the prior "
                     f"text when it parses), time {p.time}, window {p.window}, axis {p.axis}")
        lines.append(f"target: {t.kind} {t.dimension} of {t.objects}, time {t.time}, window {t.window}, axis "
                     f"{t.axis}, unit {t.unit or '-'}")
        dbg = {k: v for k, v in ans.debug.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
        if dbg:
            lines.append("numbers: " + ", ".join(f"{k}={_fmt(v)}" for k, v in sorted(dbg.items())))
        if ans.debug.get("tracks"):
            lines.append(f"objects matched to roles: {ans.debug['tracks']}")
        flags = sorted(set(a.flags) | {f"geo:{f}" for f in ans.flags})
        if flags:
            lines.append("flags: " + ", ".join(flags))
        for tr in a.tracks:
            o = tr.obs
            fr = sorted({round(x.t * self.fps) for x in o})
            lines.append(f"track {tr.role} \"{tr.object}\": {len(o)} obs ({sum(x.point is not None for x in o)} points, "
                         f"{sum(x.extent is not None for x in o)} extents, {sum(x.box is not None for x in o)} boxes), "
                         f"frames {fr[0] if fr else '-'}..{fr[-1] if fr else '-'}"
                         + (f", depth_name {tr.depth_name}" if tr.depth_name else ""))
        return "\n".join(lines)

    def submit(self, inp: dict) -> ToolOutput:
        answers = inp.get("answers")
        if not isinstance(answers, list) or not answers:
            raise ToolError("answers must be a non-empty list")
        staged, errors = {}, []
        for ans in answers:
            try:
                qid = self._qid(ans.get("qid") if isinstance(ans, dict) else None)
                direct = _num(ans.get("direct_answer"))
                conf = _num(ans.get("confidence"))
                if ans.get("spec") is not None and ans.get("tracks") is not None and not ans.get("use_last_solve"):
                    q = self._question(qid, ans["spec"], self.resolve_tracks(ans["tracks"]))
                elif qid in self.last_solve:
                    q = copy.deepcopy(self.last_solve[qid])
                else:
                    raise ToolError(f"qid {qid}: no solve call yet; give spec and tracks")
                q.update(direct_answer=direct if direct is not None and direct > 0 else None, confidence=conf,
                         derivation=str(ans.get("derivation") or "")[:400])
                self.geometry(q)   # must parse
                staged[qid] = q
            except ToolError as e:
                errors.append(str(e))
        self.submitted.update(staged)
        missing = [q for q in self.qids if q not in self.submitted]
        if not missing and not errors:
            self.done = True
            return ToolOutput([_text(f"Submitted answers for all {len(self.qids)} questions. Session complete.")],
                              False, f"submitted {sorted(staged)}; complete")
        msg = (f"Recorded answers for {sorted(staged) or 'none'}."
               + (f" Errors: {'; '.join(errors)}." if errors else "")
               + (f" Still missing: {missing}: call submit for them." if missing else ""))
        return ToolOutput([_text(msg)], bool(errors), msg[:160])

    # ----------------------------------------------------------------- final answers

    def final_parsed(self) -> tuple[dict, list[int], list[int]]:
        """({"questions": [...]} for the record, qids answered from their last solve call (no submit),
        qids with nothing)."""
        qs, fallback, missing = [], [], []
        for qid in self.qids:
            if qid in self.submitted:
                qs.append(self.submitted[qid])
            elif qid in self.last_solve:
                qs.append({**copy.deepcopy(self.last_solve[qid]), "direct_answer": None, "confidence": None,
                           "derivation": "fallback: last solve call (not submitted)"})
                fallback.append(qid)
            else:
                missing.append(qid)
        return {"questions": qs}, fallback, missing


# --------------------------------------------------------------------------- API loop

@dataclass
class AgentConfig:
    model: str = MODEL
    effort: str = "medium"
    max_turns: int = MAX_TURNS
    max_tokens: int = TURN_MAX_TOKENS
    max_usd: float = MAX_USD_VIDEO            # per video
    max_output_tokens: int = MAX_OUT_VIDEO    # per video
    strict: bool = True
    thinking_display: str = "summarized"
    task_budget: int = 0                      # API task budget (beta task-budgets-2026-03-13); 0 = off
    overview_frames: int = OVERVIEW_FRAMES
    run: str = ""                             # ledger run name
    split: str = ""

    def settings(self) -> dict:
        d = asdict(self)
        d.pop("run")
        d.pop("split")
        d["agent_version"] = AGENT_VERSION
        return d


def _plain(x):
    """SDK objects / SimpleNamespaces -> JSON-able dicts."""
    if hasattr(x, "to_dict"):
        return x.to_dict()
    if isinstance(x, dict):
        return {k: _plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_plain(v) for v in x]
    if hasattr(x, "__dict__"):
        return {k: _plain(v) for k, v in vars(x).items()}
    return x


def strip_images(obj, saved: dict | None = None):
    """A JSON-able copy of a message list without image bytes (replaced by the saved file name or a
    size) or thinking signatures."""
    obj = _plain(obj)
    if isinstance(obj, list):
        return [strip_images(x, saved) for x in obj]
    if isinstance(obj, dict):
        if obj.get("type") == "image":
            data = (obj.get("source") or {}).get("data", "")
            key = hashlib.sha1(data.encode()).hexdigest()[:16] if data else ""
            return {"type": "image", "omitted": True, "bytes": len(data) * 3 // 4,
                    **({"file": saved[key]} if saved and key in saved else {})}
        return {k: strip_images(v, saved) for k, v in obj.items() if k != "signature"}
    return obj


def estimate_content_tokens(content) -> int:
    """Offline token estimate of message content (text ~3.5 chars/token, images w*h/750)."""
    n = 0
    for b in content if isinstance(content, list) else [content]:
        b = b if isinstance(b, dict) else _plain(b)
        if not isinstance(b, dict):
            n += math.ceil(len(str(b)) / 3.5)
        elif b.get("type") == "image":
            data = base64.b64decode((b.get("source") or {}).get("data", ""))
            img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_UNCHANGED) if data else None
            n += image_tokens(img.shape[1], img.shape[0]) if img is not None else 1600
        elif b.get("type") == "tool_result":
            n += 10 + estimate_content_tokens(b.get("content") or [])
        else:
            n += math.ceil(len(json.dumps(b, default=str)) / 3.5)
    return n


TOOLS_SYSTEM_TOKENS = 8000   # tools (strict) + system prompt tokens (count_tokens: ~7.7k)


def estimate_video_usd(initial_tokens: int, n_questions: int, effort: str = "medium",
                       max_turns: int = MAX_TURNS, model: str = MODEL) -> float:
    """Expected cost of one video (prompt caching: the prefix is read each turn, each turn's new input and
    the previous output are written once)."""
    p = budget.PRICES.get(model) or max(budget.PRICES.values(), key=lambda q: q["output"])
    turns = min(max_turns, EST_TURNS.get(effort, 10) + n_questions)
    out = EST_OUT_PER_TURN.get(effort, 3000)
    ctx = initial_tokens + TOOLS_SYSTEM_TOKENS
    usd = ctx * p["cache_write_5m"]
    for _ in range(turns):
        usd += ctx * p["cache_read"] + EST_IN_PER_TURN * p["cache_write_5m"] + out * (p["output"] + p["cache_write_5m"])
        ctx += EST_IN_PER_TURN + out
    return usd / 1e6


def call_stream(client, params: dict, retries: int = 2, beta: list[str] | None = None):
    """One streamed request; returns (Message, request_id). Transient errors are retried."""
    for attempt in range(retries + 1):
        try:
            api = client.beta.messages if beta else client.messages
            kw = {**params, **({"betas": beta} if beta else {})}
            with api.stream(**kw) as stream:
                return stream.get_final_message(), getattr(stream, "request_id", None)
        except Exception as e:  # noqa: BLE001
            status = getattr(e, "status_code", None)
            transient = type(e).__name__ in ("APIConnectionError", "APITimeoutError") or (status or 0) >= 500
            if not transient or attempt == retries:
                raise
            time.sleep(10 * 2 ** attempt)
    raise AssertionError("unreachable")


def _usage_add(tot: dict, u: dict) -> None:
    for k, v in u.items():
        tot[k] = tot.get(k, 0) + int(v or 0)


def status_text(turn: int, cfg: AgentConfig, spent: float, out_tokens: int, session: AgentSession) -> str:
    left = cfg.max_turns - turn
    missing = [q for q in session.qids if q not in session.submitted]
    s = (f"[status] {turn} of {cfg.max_turns} responses used; ${spent:.2f} of ${cfg.max_usd:.2f} and "
         f"{out_tokens // 1000}k of {cfg.max_output_tokens // 1000}k output tokens used for this video; "
         f"questions without a submitted answer: {missing or 'none'}.")
    if left <= 1:
        s += " This is your last response: call submit now with your best answers for every question."
    elif left <= WRAP_UP_TURNS or spent >= WRAP_UP_FRAC * cfg.max_usd or out_tokens >= WRAP_UP_FRAC * cfg.max_output_tokens:
        s += " Wrap up now: call submit with your best answers for every question in your next response."
    return s


def run_video(client, session: AgentSession, cfg: AgentConfig, log=print) -> dict:
    """The agentic loop for one video -> record (status ok | partial | failed | refusal | error, the
    claude_annotate-format parsed answers and meta, usage, cost, transcript without image bytes, tool calls)."""
    model = cfg.model
    prices = budget.PRICES.get(model) or max(budget.PRICES.values(), key=lambda q: q["output"])
    tools = tool_definitions(cfg.strict)
    system = [{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}]
    initial = session.initial_content(cfg.overview_frames, cfg.max_turns, cfg.max_usd)
    messages: list[dict] = [{"role": "user", "content": initial}]
    output_config: dict = {"effort": cfg.effort}
    beta = None
    if cfg.task_budget:
        output_config["task_budget"] = {"type": "tokens", "total": int(cfg.task_budget)}
        beta = ["task-budgets-2026-03-13"]
    thinking = {"type": "adaptive", **({"display": cfg.thinking_display} if cfg.thinking_display else {})}
    spent, out_tokens, totals = 0.0, 0, {}
    requests, tool_calls = [], []
    stop, status_reason = "max_turns", None
    prefix_tokens = 0                                   # input of the previous request: a cache read now
    new_tokens = TOOLS_SYSTEM_TOKENS + estimate_content_tokens(initial)   # appended since: a cache write
    t_start = time.time()
    turn = 0
    for turn in range(1, cfg.max_turns + 1):
        # budget: expected input cost (cached prefix read, new part written); max_tokens shrinks to fit the cap
        in_exp = (prefix_tokens * prices["cache_read"] + new_tokens * prices["cache_write_5m"]) / 1e6
        room = cfg.max_usd - spent - in_exp
        max_tokens = int(min(cfg.max_tokens, cfg.max_output_tokens - out_tokens, room * 1e6 / prices["output"]))
        if max_tokens < MIN_TURN_TOKENS:
            stop = "budget_video"
            break
        worst = ((prefix_tokens + new_tokens) * prices["cache_write_5m"] + max_tokens * prices["output"]) / 1e6
        params = {"model": model, "max_tokens": max_tokens, "system": system, "tools": tools,
                  "messages": messages, "output_config": output_config, "thinking": thinking,
                  "cache_control": {"type": "ephemeral"}}
        try:
            with budget.reserve(worst):
                msg, request_id = call_stream(client, params, beta=beta)
                usd = budget.price(msg.usage, model)
                budget.record(cfg.run, model, "sync", request_id or msg.id, msg.usage, usd,
                              video_id=session.video_id, split=cfg.split, turn=turn, agent=AGENT_VERSION)
        except budget.BudgetExceeded as e:
            stop, status_reason = "budget_global", str(e)
            break
        except Exception as e:  # noqa: BLE001 - keep what was measured so far
            stop, status_reason = "api_error", f"{type(e).__name__}: {e}"
            log(f"  {session.video_id}: turn {turn}: {status_reason}")
            break
        u = budget.usage_dict(msg.usage)
        _usage_add(totals, u)
        spent += usd
        out_tokens += u["output_tokens"]
        prefix_tokens = u["input_tokens"] + u["cache_read_input_tokens"] + u["cache_creation_input_tokens"]
        content = list(msg.content)
        messages.append({"role": "assistant", "content": content})   # unchanged (thinking blocks included)
        uses = [b for b in content if getattr(b, "type", None) == "tool_use"]
        requests.append({"turn": turn, "request_id": request_id, "message_id": getattr(msg, "id", None),
                         "stop_reason": msg.stop_reason, "max_tokens": max_tokens, "usage": u, "usd": round(usd, 6),
                         "tools": [b.name for b in uses], "seconds": round(time.time() - t_start, 1)})
        if msg.stop_reason == "refusal":
            stop, status_reason = "refusal", str(_plain(getattr(msg, "stop_details", None)))
            break
        if not uses:
            if session.done:
                stop = "submitted"
                break
            nudge = ("You did not call a tool. Measure with the tools, or call submit with your answers for "
                     "every question." if msg.stop_reason != "max_tokens" else
                     "Your response hit max_tokens. Continue with shorter tool calls; submit soon.")
            messages.append({"role": "user", "content": [_text(nudge + " "
                                                               + status_text(turn, cfg, spent, out_tokens, session))]})
            new_tokens = estimate_content_tokens(messages[-1]["content"]) + u["output_tokens"]
            continue
        results = []
        for b in uses:
            t0 = time.time()
            if msg.stop_reason == "max_tokens":
                out = ToolOutput([_text("Your response hit max_tokens before this call was complete; call it again "
                                        "(shorter).")], True, "cut off by max_tokens")
            else:
                out = session.execute(b.name, _plain(b.input))
            tool_calls.append({"turn": turn, "id": b.id, "name": b.name, "input": _plain(b.input),
                               "is_error": out.is_error, "summary": out.summary,
                               "seconds": round(time.time() - t0, 2)})
            results.append({"type": "tool_result", "tool_use_id": b.id, "content": out.content,
                            **({"is_error": True} if out.is_error else {})})
        if session.done:
            stop = "submitted"
            break
        user = results + [_text(status_text(turn, cfg, spent, out_tokens, session))]
        messages.append({"role": "user", "content": user})
        new_tokens = estimate_content_tokens(user) + u["output_tokens"]
    parsed, fallback, missing = session.final_parsed()
    answered = len(parsed["questions"])
    if stop == "refusal" and not answered:
        status = "refusal"
    elif not answered:
        status = "failed"
    elif fallback or missing:
        status = "partial"
    else:
        status = "ok"
    final = {}
    for q in parsed["questions"]:
        try:
            a, ans = session.geometry(q)
            final[q["qid"]] = {"geo": ans.value, "method": ans.method, "flags": ans.flags,
                               "direct": q.get("direct_answer")}
        except Exception as e:  # noqa: BLE001
            final[q["qid"]] = {"error": f"{type(e).__name__}: {e}"}
    return {"video_id": session.video_id, "status": status, "stop": stop, "stop_detail": status_reason,
            "model": model, "effort": cfg.effort, "config": cfg.settings(), "agent_version": AGENT_VERSION,
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "turns": len(requests),
            "usage": totals, "usd": round(spent, 6), "requests": requests, "tool_calls": tool_calls,
            "tool_counts": dict(Counter(c["name"] for c in tool_calls)),
            "missing_qids": missing, "fallback_qids": fallback, "meta": session.meta(), "parsed": parsed,
            "final_geometry": final, "measurements": {k: {"kind": m.kind, "object": m.object, "info": m.info,
                                                          "n_obs": len(m.obs)} for k, m in session.meas.items()},
            "transcript": strip_images([{"role": "system", "content": SYSTEM[:200] + " ..."}] + messages, session.saved),
            "seconds": round(time.time() - t_start, 1)}
