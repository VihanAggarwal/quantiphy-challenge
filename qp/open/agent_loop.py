"""Per-clip agentic measurement with an OPEN-WEIGHT multimodal model (Track B, RUN_PRESET "agent").

The Track A agentic run (research/blind/annotate_v3.workflow.js) gave one Claude agent per clip a blind workspace
(the video + inputs.json, no labels), a frame viewer and a Python/OpenCV sandbox, and let it measure with pinhole
geometry in code. This module does the same with an open-weight model (default Qwen/Qwen3.6-27B-FP8, Apache-2.0)
served by vLLM (the offline engine of qp.open.ctx_annot.CtxVLLM: several images per prompt, per-request thinking).
No closed model is called anywhere.

Protocol (plain text, robust for a ~27B model): every assistant reply ends with exactly ONE action
    ```python ... ```                 run Python in a subprocess, cwd = the clip workspace (timeout, output truncated)
    FRAME <t> [x0 y0 x1 y1] [scale]   the frame at time t (FRAME #<idx> for an index), full frame or zoomed crop,
                                      with a labelled pixel grid in ORIGINAL coordinates ("nogrid" to switch it off)
    ANSWERS {"<qid>": <number>, ...}  final answers (positive magnitudes in the asked unit); ends the clip
The reply to an action is one user message: text (+ images for FRAME and for show() calls in Python).
Caps: steps (default 30), time per clip (default 8 min of the clip's OWN time: its share of each batched generate()
call + its tool runs, i.e. about what the clip would take alone; real elapsed time is capped at 4x that), context
budget, consecutive malformed replies; on any
cap the model gets one forced "ANSWERS only" turn (no thinking, greedy). Answers are parsed leniently, made positive
(abs), non-finite / zero values dropped; qids still missing are left to the fallback (run_agent.py / build_sub.py).

Scheduling: many clip conversations run at once. The loop gathers every conversation that waits for the model and
sends them to the backend in ONE generate() call (vLLM batches them), while tool calls (Python, frames) run in a
thread pool, so a slow sandbox never blocks the GPU batch. A clip's answers + transcript are written atomically when
it finishes; finished clips are skipped on the next run (resumable).

Backend contract: backend.generate(list[CtxRequest]) -> list[str | None] (None = failed generation).
"""

from __future__ import annotations

import json
import math
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from collections import deque
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from qp.open.ctx_annot import CtxRequest
from qp.open.qwen_vl import _balanced, _loads

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = "Qwen/Qwen3.6-27B-FP8"
FALLBACK_MODEL = "Qwen/Qwen3.6-27B"
PROMPT_VERSION = "agent-v1"

# sampling (Qwen3.6 model card): thinking for precise tasks; non-thinking general; greedy for the forced final turn
THINK_SAMPLING = {"temperature": 0.6, "top_p": 0.95, "top_k": 20}
PLAIN_SAMPLING = {"temperature": 0.7, "top_p": 0.8, "top_k": 20}
FINAL_SAMPLING = {"temperature": 0.0, "top_p": 1.0, "top_k": -1}


@dataclass
class AgentConfig:
    max_steps: int = 30                 # actions per clip (the forced final turn comes on top)
    max_wall_s: float = 480.0           # time per clip: the clip's OWN model + tool time (see Conversation.active_s)
    max_elapsed_factor: float = 4.0     # safety cap on real elapsed time per clip = factor x max_wall_s
    py_timeout: float = 60.0            # seconds per Python run
    obs_chars: int = 4096               # stdout + stderr returned per run (head + tail)
    thinking: bool = True               # reason before each action (cut replies retry the turn without)
    max_tokens_think: int = 8192
    max_tokens_plain: int = 3072
    max_tokens_final: int = 1536
    max_model_len: int = 65536          # context budget (must match the engine)
    max_images: int = 12                # images per prompt (engine limit_mm_per_prompt)
    keep_images: int = 8                # when over max_images, the oldest are dropped down to this many
    frame_max_side: int = 1280          # long side of every image sent
    show_per_run: int = 2               # images a Python run may attach with show()
    max_malformed: int = 4              # consecutive replies without an action -> forced final
    max_failed: int = 3                 # consecutive failed generations (None) -> clip given up (fallback)
    mem_mb: int = 16384                 # address-space limit of a Python run
    ws_warn_mb: int = 300               # workspace size warning
    seed: int = 0


# --------------------------------------------------------------------------- prompt

def system_prompt(cfg: AgentConfig) -> str:
    return f"""\
You are a meticulous measurement agent for the QuantiPhy benchmark. You answer every question about ONE video as \
accurately as possible by measuring the video with code. Answers are scored by relative error: under 5% error is full \
credit, 10% ~0.9, 20% ~0.8, 50% ~0.4, 100% or more 0.

## Actions
End EVERY reply with exactly ONE action. Write brief reasoning first; write nothing after the action.

1. Run Python: one fenced block
```python
from qptools import *
print(W, H, N, FPS)
```
It runs as a fresh process in your workspace folder (the current directory), {cfg.py_timeout:g} s limit, no network, \
no GPU; numpy, cv2 (OpenCV), scipy and pandas are installed. You only get stdout/stderr back (at most \
{cfg.obs_chars} characters): print compact numbers, not whole arrays. Variables do not persist between runs; save \
intermediate results as small .json/.npy files in the workspace when you need them later. Keep scratch under 100 MB: \
read frames from the video inside your script, never save every frame.
`from qptools import *` gives: VIDEO (video path), FPS (the dataset frame rate: use it, not the container's), W, H \
(frame size), N (frame count), QUESTIONS (the questions), t2i(t) = round(t*FPS) (frame index at time t), frame(i) -> \
BGR uint8 image of frame index i, frames(i0=0, i1=None, step=1, gray=False) -> iterator of (i, image), \
show(img, label) -> attaches an image you made (e.g. a mask or track overlay) to the result so you can look at it \
(max {cfg.show_per_run} per run), grid(img, step=50) -> copy with a labelled pixel grid.

2. Look at a frame: one line
FRAME <t> [x0 y0 x1 y1] [scale]
Shows the frame at time t seconds (frame index round(t*FPS); write FRAME #<index> for an index): the full frame, or \
the crop x0..x1, y0..y1 (ORIGINAL pixel coordinates) enlarged by scale (2-4 for precise ends and edges). A pixel grid \
labelled in ORIGINAL frame coordinates is drawn; add the word nogrid for a clean image. Images are at most \
{cfg.frame_max_side} px on the long side.

3. Final answers: the word ANSWERS and one JSON object mapping EVERY qid to one positive number in the unit the \
question asks for (target_unit)
ANSWERS {{"12": 3.4, "13": 0.85}}
This ends the task. Send it when your measurements are done, before the budget runs out.

Budget: at most {cfg.max_steps} actions and about {cfg.max_wall_s / 60:.0f} minutes for this video; every result \
tells you how many actions are left.

## How the true answers were made (dataset paper)
- The prior is exactly true for this video. Scenes can be scaled arbitrarily: the prior (and depth_info) is the \
scale; use real-world plausibility only as a sanity check, never as the answer.
- Blender simulation (video_source simulation / segmentation): fixed camera with UNKNOWN focal length (horizontal \
FOV 8-103 deg). depth_info is documented as the Euclidean distance from the camera to the object's ORIGIN (humans: \
pelvis; vehicles: body centre / rig root), but VERIFY which convention (range vs optical-axis depth Z) fits the scene \
geometry and use the consistent one. Sizes = world axis-aligned bounding-box dimensions. Speed at t = backward \
difference of the origin position, |p(t) - p(t - 1 frame)| * fps. Acceleration = change of the speed magnitude per \
second. 2D videos are planar views: one metres-per-pixel scale from the prior (size prior: its pixel extent; speed \
prior: its pixel speed; acceleration prior: its pixel acceleration), but objects at different depths or seen at an \
angle can still have different scales: check perspective cues.
- Internet videos: real footage; the prior is the scale; the camera may move: check for camera motion before \
measuring motion.
- Lab videos: real camera, horizontal FOV ~84 deg (f ~711 px at 1280 px width; f scales with the frame width), \
labels from hand-clicked centres + ToF depth, forward differences at 25 fps.
- Segmented videos = the same footage with the background removed.

## Method
1. Look at full frames (start, middle, end, every asked time); identify every object named in the questions and the \
prior. Measure extents on zoomed crops and read coordinates off the grid.
2. Prefer code over eyeballing: with a static camera use background subtraction / frame differencing, colour \
thresholds, contours or template matching for precise masks, centres and extents per frame. Verify masks by drawing \
overlays and show()-ing them.
3. Scale: 3D -> pinhole model with depth_info; recover the camera (focal length, horizon / vanishing points from \
straight lines, camera height from the ground plane) and cross-check the focal length by two independent routes. \
2D -> metres per pixel from the prior.
4. Compute every answer in code; for motion use the dataset's difference convention around the asked time with light \
smoothing of the measured track. Cross-check by a second route and for physical consistency across the questions.
5. Answers are POSITIVE magnitudes in the asked unit. Never answer 0 or a negative number; when unsure, still give \
your best estimate."""


FINAL_PROMPT = ("STOP: {reason}. Reply now with ONLY the final line\nANSWERS {{...}}\nmapping EVERY qid ({qids}) to "
                "your best positive estimate in the asked unit. No code, no other text.")
NO_ACTION = ("No action found in your reply. End every reply with exactly one action: a ```python``` block, a "
             "FRAME <t> [x0 y0 x1 y1] [scale] line, or ANSWERS {...}.")
CUT_REPLY = ("Your reply was cut off before an action (too long). Keep the reasoning short and end with exactly one "
             "action.")


# --------------------------------------------------------------------------- clips and workspaces

@dataclass
class Clip:
    video_id: str
    video_path: str
    questions: list[dict]             # qid, question, prior, depth_info, fps, video_type, target_unit, video_source
    reuse: dict = field(default_factory=dict)   # qid -> (source video_id, source qid): answered by a twin

    @property
    def qids(self) -> list[int]:
        return [int(q["qid"]) for q in self.questions]


def _s(x) -> str:
    return "" if x is None or (isinstance(x, float) and math.isnan(x)) else str(x).strip()


def clips_from_df(df) -> list[Clip]:
    """qp.data rows (answers dropped by the caller) -> one Clip per video, in first-appearance order."""
    out = []
    for vid, g in df.groupby("video_id", sort=False):
        qs = [{"qid": int(r.qid), "question": _s(r.question), "prior": _s(r.prior), "depth_info": _s(r.depth_info),
               "fps": float(r.fps) if r.fps == r.fps else None, "video_type": _s(r.video_type),
               "target_unit": _s(getattr(r, "target_unit", "")), "video_source": _s(getattr(r, "video_source", ""))}
              for r in g.itertuples(index=False)]
        out.append(Clip(str(vid), str(g.video_path.iloc[0]), qs))
    return out


def norm_question(q: str) -> str:
    from qp.postprocess import norm_question as nq
    return nq(q)


def plan_twins(clips: list[Clip]) -> list[Clip]:
    """Segmented twins (<video>_segmented, same footage with the background removed) reuse the original clip's answer
    to the same normalised question (research/blind/build_agent_sub.py) when the original is in the same split: those
    questions are moved to Clip.reuse and not asked again. A twin with no question left keeps no questions (it is
    filled from the original after the run)."""
    by_id = {c.video_id: c for c in clips}
    for c in clips:
        if not c.video_id.endswith("_segmented"):
            continue
        o = by_id.get(c.video_id[: -len("_segmented")])
        if o is None:
            continue
        omap = {norm_question(q["question"]): q["qid"] for q in o.questions}
        keep = []
        for q in c.questions:
            j = omap.get(norm_question(q["question"]))
            if j is None:
                keep.append(q)
            else:
                c.reuse[int(q["qid"])] = (o.video_id, int(j))
        if c.reuse:
            c.questions = keep
    return clips


def safe_id(video_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", str(video_id).strip())[:80] or "video"


def video_meta(path: str) -> tuple[int, int, int, float]:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise FileNotFoundError(path)
    n, w, h = (int(cap.get(p)) for p in (cv2.CAP_PROP_FRAME_COUNT, cv2.CAP_PROP_FRAME_WIDTH,
                                         cv2.CAP_PROP_FRAME_HEIGHT))
    cfps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    if n <= 0:
        n = 0
        while cap.grab():
            n += 1
    cap.release()
    return n, w, h, cfps


QPTOOLS = '''"""Helpers for measurement scripts in this workspace:  from qptools import *"""
import json
from pathlib import Path

import cv2
import numpy as np

_D = Path(__file__).resolve().parent
INPUTS = json.loads((_D / "inputs.json").read_text())
VIDEO = str(_D / INPUTS["video_file"])
FPS = float(INPUTS["fps"])
W, H, N = int(INPUTS["width"]), int(INPUTS["height"]), int(INPUTS["n_frames"])
QUESTIONS = INPUTS["questions"]
__all__ = ["INPUTS", "VIDEO", "FPS", "W", "H", "N", "QUESTIONS", "t2i", "i2t", "frame", "frames", "show", "grid",
           "cv2", "np", "json"]


def t2i(t):
    """frame index at time t seconds (dataset convention: round(t * FPS))"""
    return int(round(float(t) * FPS))


def i2t(i):
    return float(i) / FPS


def frame(i, gray=False):
    """BGR uint8 frame of index i (clipped to the video)."""
    i = int(min(max(int(i), 0), N - 1))
    cap = cv2.VideoCapture(VIDEO)
    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
    ok, im = cap.read()
    cap.release()
    if not ok:
        raise IndexError(f"cannot read frame {i}")
    return cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) if gray else im


def frames(i0=0, i1=None, step=1, gray=False):
    """iterate (index, BGR frame) for i0 <= index < i1 (default: to the end), every `step` frames"""
    i1 = N if i1 is None else min(int(i1), N)
    cap = cv2.VideoCapture(VIDEO)
    if i0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i0))
    i = int(i0)
    while i < i1:
        ok, im = cap.read()
        if not ok:
            break
        if (i - i0) % step == 0:
            yield i, (cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) if gray else im)
        i += 1
    cap.release()


def grid(img, step=50):
    """copy of img with a labelled pixel grid every `step` px"""
    im = img.copy() if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    h, w = im.shape[:2]
    for x in range(0, w, int(step)):
        cv2.line(im, (x, 0), (x, h), (0, 255, 255), 1)
        cv2.putText(im, str(x), (x + 2, 12), 0, 0.4, (0, 255, 255), 1)
    for y in range(0, h, int(step)):
        cv2.line(im, (0, y), (w, y), (0, 255, 255), 1)
        cv2.putText(im, str(y), (2, y + 12), 0, 0.4, (0, 255, 255), 1)
    return im


_SHOWN = [0]


def show(img, label=""):
    """attach an image (BGR / gray / bool / float array) to this run's result (the first few calls only)"""
    a = np.asarray(img)
    if a.dtype == bool:
        a = a.astype(np.uint8) * 255
    elif a.dtype != np.uint8:
        a = a.astype(float)
        lo, hi = np.nanmin(a), np.nanmax(a)
        a = np.zeros(a.shape, np.uint8) if hi <= lo else ((a - lo) / (hi - lo) * 255).astype(np.uint8)
    d = _D / "_show"
    d.mkdir(exist_ok=True)
    k = _SHOWN[0]
    _SHOWN[0] += 1
    cv2.imwrite(str(d / f"{k:02d}.png"), a)
    (d / f"{k:02d}.txt").write_text(str(label)[:200])
'''

GUARD = '''"""Sandbox guard, imported before every script of this workspace: no network, no reads outside the workspace's
allowed roots. Not a security boundary - a guard against accidental use of other files (labels, other clips)."""
import builtins
import io
import os
import socket
import sys

try:
    import resource
    _mb = int(os.environ.get("QP_MEM_MB", "0"))
    if _mb > 0:
        resource.setrlimit(resource.RLIMIT_AS, (_mb * 2**20, _mb * 2**20))
    resource.setrlimit(resource.RLIMIT_FSIZE, (512 * 2**20, 512 * 2**20))
except Exception:
    pass

_WS = os.path.realpath(os.getcwd())
_ALLOW = [_WS] + [os.path.realpath(p) for p in os.environ.get("QP_ALLOW", "").split(os.pathsep) if p]
_DENY = [os.path.realpath(p) for p in os.environ.get("QP_DENY", "").split(os.pathsep) if p]


def _under(p, roots):
    return any(p == r or p.startswith(r.rstrip(os.sep) + os.sep) for r in roots)


def _check(path):
    if isinstance(path, int):
        return
    try:
        p = os.path.realpath(os.fspath(path))
    except TypeError:
        return
    if not _under(p, _ALLOW) and _under(p, _DENY):
        raise PermissionError(f"outside the workspace: {path}")


def _wrap(fn):
    def g(*a, **k):
        _check(a[0] if a else k.get("file", k.get("path", ".")))
        return fn(*a, **k)
    return g


builtins.open = io.open = _wrap(io.open)
for _n in ("listdir", "scandir", "open"):
    setattr(os, _n, _wrap(getattr(os, _n)))


def _blocked(*a, **k):
    raise PermissionError("network access is disabled in this sandbox")


_orig_connect = socket.socket.connect


def _connect(self, addr):
    if self.family == getattr(socket, "AF_UNIX", None):
        return _orig_connect(self, addr)
    _blocked()


socket.socket.connect = _connect
socket.socket.connect_ex = lambda self, addr: _connect(self, addr)
socket.create_connection = _blocked
'''


def prepare_workspace(clip: Clip, ws: Path, fps_fallback: float | None = None) -> dict:
    """Fresh workspace: the video (copied, so nothing outside the workspace is needed), inputs.json, qptools.py and
    the guard. Returns the inputs dict."""
    if ws.exists():
        shutil.rmtree(ws)
    ws.mkdir(parents=True)
    src = Path(clip.video_path)
    vf = "video" + (src.suffix or ".mp4")
    try:
        os.link(src, ws / vf)
    except OSError:
        shutil.copy2(src, ws / vf)
    n, w, h, cfps = video_meta(str(ws / vf))
    fps = next((float(q["fps"]) for q in clip.questions if q.get("fps") and q["fps"] > 0), None) \
        or fps_fallback or cfps or 30.0
    inputs = {"video_id": clip.video_id, "video_file": vf, "width": w, "height": h, "n_frames": n, "fps": fps,
              "container_fps": cfps, "duration_s": n / fps, "questions": clip.questions}
    (ws / "inputs.json").write_text(json.dumps(inputs, indent=1))
    (ws / "qptools.py").write_text(QPTOOLS)
    (ws / "_qp_guard.py").write_text(GUARD)
    return inputs


# --------------------------------------------------------------------------- frames

def _nice_step(span_px: float, target_lines: int = 12) -> int:
    raw = max(1.0, span_px / target_lines)
    for s in (1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000):
        if s >= raw:
            return s
    return 1000


def read_frame(path: str, idx: int) -> np.ndarray | None:
    cap = cv2.VideoCapture(path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
    ok, im = cap.read()
    cap.release()
    return im if ok else None


def _to_pil(bgr: np.ndarray, max_side: int):
    from PIL import Image
    h, w = bgr.shape[:2]
    s = min(1.0, max_side / max(h, w))
    if s < 1.0:
        bgr = cv2.resize(bgr, (max(1, round(w * s)), max(1, round(h * s))), interpolation=cv2.INTER_AREA)
    if bgr.ndim == 2:
        bgr = cv2.cvtColor(bgr, cv2.COLOR_GRAY2BGR)
    return Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))


def _label(img: np.ndarray, text: str, org: tuple[int, int], fs: float) -> None:
    """yellow text with a black outline (readable on bright and dark backgrounds)"""
    cv2.putText(img, text, org, 0, fs, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(img, text, org, 0, fs, (0, 255, 255), 1, cv2.LINE_AA)


def render_frame(path: str, fps: float, n_frames: int, t: float | None = None, idx: int | None = None,
                 box: list[float] | None = None, scale: float = 1.0, draw_grid: bool = True,
                 max_side: int = 1280):
    """(PIL image, caption) of one frame, full or a crop (original pixel box) enlarged by `scale`, with a grid
    labelled in ORIGINAL frame coordinates; the result is shrunk to `max_side` if needed (caption says so)."""
    if idx is None:
        idx = int(round(float(t) * fps))
    idx = int(min(max(idx, 0), max(n_frames - 1, 0)))
    im = read_frame(path, idx)
    if im is None:
        raise ValueError(f"cannot read frame {idx}")
    H, W = im.shape[:2]
    x0, y0, x1, y1 = 0, 0, W, H
    if box:
        x0, x1 = sorted((int(round(box[0])), int(round(box[2]))))
        y0, y1 = sorted((int(round(box[1])), int(round(box[3]))))
        x0, x1 = max(0, min(x0, W - 1)), max(1, min(x1, W))
        y0, y1 = max(0, min(y0, H - 1)), max(1, min(y1, H))
        if x1 - x0 < 4 or y1 - y0 < 4:
            raise ValueError(f"crop {box} is empty inside the {W}x{H} frame")
        im = im[y0:y1, x0:x1]
    scale = float(min(max(scale, 0.1), 8.0))
    cw, ch = x1 - x0, y1 - y0
    shown = scale * min(1.0, max_side / (max(cw, ch) * scale))
    out = cv2.resize(im, (max(1, round(cw * shown)), max(1, round(ch * shown))),
                     interpolation=cv2.INTER_CUBIC if shown > 1 else cv2.INTER_AREA)
    step = None
    if draw_grid:
        step = _nice_step(max(cw, ch))
        fs = 0.4 if max(out.shape[:2]) < 900 else 0.5
        for gx in range((x0 // step + 1) * step if x0 % step else x0, x1, step):
            px = int(round((gx - x0) * shown))
            cv2.line(out, (px, 0), (px, out.shape[0]), (0, 255, 255), 1)
            _label(out, str(gx), (px + 2, 13), fs)
        for gy in range((y0 // step + 1) * step if y0 % step else y0, y1, step):
            py = int(round((gy - y0) * shown))
            cv2.line(out, (0, py), (out.shape[1], py), (0, 255, 255), 1)
            _label(out, str(gy), (2, py + 13), fs)
    img = _to_pil(out, max_side)
    what = f"crop x {x0}..{x1}, y {y0}..{y1} of the {W}x{H} frame" if box else f"full {W}x{H} frame"
    cap = (f"Frame #{idx} (t={idx / fps:.3f} s): {what}, shown at {shown:.3g}x ({img.size[0]}x{img.size[1]} px)"
           + (f"; grid lines every {step} px, labels = ORIGINAL frame pixel coordinates" if step else "; no grid"))
    return img, cap


def contact_sheet(path: str, fps: float, n_frames: int, max_side: int = 1280, k: int = 4):
    """2x2 overview of k uniform frames (orientation only; coordinates are not original)."""
    idxs = sorted(set(np.linspace(0, max(n_frames - 1, 0), k).round().astype(int).tolist()))
    tiles = []
    for i in idxs:
        im = read_frame(path, i)
        if im is None:
            continue
        im = im.copy()
        cv2.putText(im, f"#{i} t={i / fps:.2f}s", (10, 40), 0, 1.2, (0, 0, 0), 5, cv2.LINE_AA)
        cv2.putText(im, f"#{i} t={i / fps:.2f}s", (10, 40), 0, 1.2, (0, 255, 255), 2, cv2.LINE_AA)
        tiles.append(im)
    if not tiles:
        raise ValueError("no frame decoded")
    h, w = tiles[0].shape[:2]
    tiles = [cv2.resize(t, (w, h)) for t in tiles] + [np.zeros((h, w, 3), np.uint8)] * (4 - len(tiles))
    sheet = np.vstack([np.hstack(tiles[:2]), np.hstack(tiles[2:4])])
    return _to_pil(sheet, max_side), [i for i in idxs]


# --------------------------------------------------------------------------- sandbox

def _truncate(text: str, n: int) -> str:
    if len(text) <= n:
        return text
    h = n // 2
    return text[:h] + f"\n... [{len(text) - 2 * h} characters omitted] ...\n" + text[-h:]


def _size(p: Path) -> int:
    try:
        return p.stat().st_size
    except OSError:
        return 0


def _read_capped(p: Path, n: int) -> str:
    """the file if it has at most n bytes, else its first and last n/2 bytes with the omitted count"""
    try:
        size = p.stat().st_size
        with open(p, "rb") as f:
            if size <= n:
                return f.read().decode("utf-8", "replace")
            h = max(1, n // 2)
            head = f.read(h).decode("utf-8", "replace")
            f.seek(size - h)
            tail = f.read().decode("utf-8", "replace")
        return head + f"\n... [{size - 2 * h} bytes omitted] ...\n" + tail
    except OSError:
        return ""


_BOOT_TB = re.compile(r'  File "<string>", line 1.*?(?=  File "_step)', re.S)


def sandbox_env(ws: Path, deny: list[str], mem_mb: int) -> dict:
    """A minimal environment: no tokens or API keys of the parent, no GPU, few threads."""
    import site
    allow = {sys.prefix, sys.base_prefix, sys.exec_prefix, *site.getsitepackages()}
    try:
        allow.add(site.getusersitepackages())
    except Exception:  # noqa: BLE001
        pass
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(ws), "LANG": "C.UTF-8",
           "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0", "MPLBACKEND": "Agg", "CUDA_VISIBLE_DEVICES": "",
           "OMP_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2", "MKL_NUM_THREADS": "2", "OPENCV_LOG_LEVEL": "ERROR",
           "QP_MEM_MB": str(int(mem_mb)), "QP_ALLOW": os.pathsep.join(sorted(a for a in allow if a)),
           "QP_DENY": os.pathsep.join(deny), "TMPDIR": str(ws)}
    if os.environ.get("LD_LIBRARY_PATH"):
        env["LD_LIBRARY_PATH"] = os.environ["LD_LIBRARY_PATH"]
    return env


def run_python(code: str, ws: Path, step: int, timeout: float = 60.0, max_chars: int = 4096,
               deny: list[str] | None = None, mem_mb: int = 16384, python: str | None = None,
               show_max: int = 2, max_side: int = 1280) -> tuple[str, list, list[str]]:
    """Run `code` in a fresh interpreter with cwd = ws -> (observation text, images, image captions)."""
    script = ws / f"_step{step:02d}.py"
    script.write_text(code)
    show_dir = ws / "_show"
    shutil.rmtree(show_dir, ignore_errors=True)
    out_p, err_p = ws / "_stdout.txt", ws / "_stderr.txt"
    boot = f"import _qp_guard, runpy; runpy.run_path({script.name!r}, run_name='__main__')"
    t0 = time.time()
    timed_out = False
    with open(out_p, "wb") as fo, open(err_p, "wb") as fe:
        proc = subprocess.Popen([python or sys.executable, "-c", boot], cwd=str(ws), stdout=fo, stderr=fe,
                                stdin=subprocess.DEVNULL, env=sandbox_env(ws, deny or [], mem_mb),
                                start_new_session=True)
        try:
            rc = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                proc.kill()
            rc = proc.wait()
    dt = time.time() - t0
    n_out, n_err = _size(out_p), _size(err_p)
    err_budget = min(n_err, max_chars // 3) if n_out else min(n_err, max_chars)
    text = _read_capped(out_p, max(256, max_chars - err_budget))
    se = _BOOT_TB.sub("", _read_capped(err_p, max(256, max_chars - min(n_out, max_chars - err_budget))))
    head = (f"TIMEOUT after {timeout:g} s (process killed; make the script faster: fewer frames, smaller crops)"
            if timed_out else f"exit code {rc} ({dt:.1f} s)")
    parts = [f"Python result: {head}", "stdout:\n" + (text.rstrip() or "(empty)")]
    if se.strip():
        parts.append("stderr:\n" + se.rstrip())
    imgs, caps = [], []
    if show_dir.is_dir():
        pngs = sorted(show_dir.glob("*.png"))
        for p in pngs[:show_max]:
            im = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
            if im is None:
                continue
            lab = (p.with_suffix(".txt").read_text() if p.with_suffix(".txt").exists() else "").strip()
            imgs.append(_to_pil(im, max_side))
            caps.append(f"show() image {p.stem}: {lab or 'no label'} ({im.shape[1]}x{im.shape[0]} px"
                        f"{', shrunk to ' + str(max_side) + ' px' if max(im.shape[:2]) > max_side else ''})")
        if len(pngs) > show_max:
            caps.append(f"({len(pngs) - show_max} more show() images were not attached; max {show_max} per run)")
        shutil.rmtree(show_dir, ignore_errors=True)
    for p in (out_p, err_p):
        p.unlink(missing_ok=True)
    return "\n".join(parts), imgs, caps


def dir_mb(d: Path, skip: str = "") -> float:
    tot = 0
    for root, _, files in os.walk(d):
        for f in files:
            if f == skip:
                continue
            try:
                tot += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return tot / 2**20


# --------------------------------------------------------------------------- parsing

_THINK_CLOSE = "</think>"
_FENCE_PY = re.compile(r"```[ \t]*(python3?|py)?[ \t]*\r?\n(.*?)(?:```|\Z)", re.S | re.I)
_FRAME = re.compile(r"^[ \t>*`\-]*(?:[Aa]ction\s*:?[ \t*`]*)?FRAME\b[ \t:]*(.*)$", re.M)
_ANS = re.compile(r"\bANSWERS\b[*`\s:=]*", re.I)
_NUM = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


@dataclass
class Action:
    kind: str                 # "python" | "frame" | "answers" | "none"
    payload: Any = None
    n_actions: int = 0        # actions found in the reply (only the first is executed)
    error: str = ""


def split_reply(text: str | None, thinking: bool) -> tuple[str, str, bool]:
    """(thinking, visible answer, ok). A thinking turn must close its thinking (</think>); otherwise it was cut at
    max_tokens and has no usable answer. Non-thinking turns: the whole text (a stray think block is removed)."""
    if text is None:
        return "", "", False
    t = str(text)
    if _THINK_CLOSE in t:
        head, ans = t.rsplit(_THINK_CLOSE, 1)
        return head.replace("<think>", "").strip(), ans.strip(), True
    if "<think>" in t or thinking:
        return t.replace("<think>", "").strip(), "", False
    return "", t.strip(), True


def _value(x) -> float | None:
    if isinstance(x, bool):
        return None
    if isinstance(x, dict):
        for k in ("value", "answer", "val", "estimate", "number"):
            if k in x:
                return _value(x[k])
        return None
    if isinstance(x, (list, tuple)):
        return _value(x[0]) if x else None
    if isinstance(x, (int, float)):
        v = float(x)
    elif isinstance(x, str):
        m = _NUM.search(x.replace(",", ""))
        if not m:
            return None
        v = float(m.group(0))
    else:
        return None
    v = abs(v)
    return v if math.isfinite(v) and v > 0 else None


def _qid(k) -> int | None:
    if isinstance(k, bool):
        return None
    if isinstance(k, int):
        return k
    m = re.search(r"\d+", str(k))
    return int(m.group(0)) if m else None


def answers_from_obj(obj, qids: list[int]) -> dict[int, float]:
    want, out = set(qids), {}
    if isinstance(obj, dict) and isinstance(obj.get("answers"), (dict, list)):
        obj = obj["answers"]
    if isinstance(obj, dict):
        items = obj.items()
    elif isinstance(obj, list):
        items = [((o.get("qid") if isinstance(o, dict) else None), o) for o in obj]
    else:
        return out
    for k, x in items:
        q = _qid(k)
        v = _value(x)
        if q in want and v is not None:
            out[q] = v
    return out


def _json_after(text: str, start: int):
    i = text.find("{", start)
    if i < 0:
        return None, -1
    sub = _balanced(text, i)
    if sub is None:            # cut or unbalanced: try to close it
        sub = text[i:].split("```")[0].rstrip().rstrip(",") + "}"
    return _loads(sub), i


def parse_answers(text: str, qids: list[int], anywhere: bool = False) -> dict[int, float]:
    """Answers from an ANSWERS block (lenient: fenced, single quotes, int keys, trailing commas, unit strings, a list
    of {qid, answer} objects, a cut-off object). anywhere=True (forced final turn): also any JSON object in the text,
    then "qid: number" pairs."""
    if not text:
        return {}
    best: dict[int, float] = {}
    for m in _ANS.finditer(text):
        obj, _ = _json_after(text, m.end())
        got = answers_from_obj(obj, qids)
        if len(got) > len(best):
            best = got
    if best or not anywhere:
        return best
    for i in [i for i, c in enumerate(text) if c == "{"][:32]:
        sub = _balanced(text, i)
        got = answers_from_obj(_loads(sub) if sub else None, qids)
        if len(got) > len(best):
            best = got
    if not best:
        want = set(qids)
        for m in re.finditer(r"(?:qid\s*)?[\"']?(\d+)[\"']?\s*[:=]\s*[\"']?([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)",
                             text):
            q, v = int(m.group(1)), _value(m.group(2))
            if q in want and v is not None and q not in best:
                best[q] = v
    return best


def parse_frame_args(s: str) -> dict:
    """'1.5', 't=1.5 100 200 300 400 2', '#37 box=[10,20,30,40] scale=3 nogrid' -> {t | idx, box, scale, grid}."""
    s = s.strip().strip("`*").strip()
    out: dict[str, Any] = {"grid": not re.search(r"\bno[ _-]?grid\b", s, re.I)}
    s = re.sub(r"\bno[ _-]?grid\b", " ", s, flags=re.I)
    m = re.search(r"scale\s*[=:]\s*([0-9.]+)", s, re.I)
    if m:
        out["scale"] = float(m.group(1))
        s = s[:m.start()] + " " + s[m.end():]
    m = re.search(r"(?:#|\bidx\s*[=:]\s*|\bindex\s*[=:]\s*|\bframe\s*[=:]\s*)(\d+)", s, re.I)
    if m:
        out["idx"] = int(m.group(1))
        s = s[:m.start()] + " " + s[m.end():]
    nums = [float(x) for x in _NUM.findall(s.replace("s ", " ").replace(",", " "))]
    if "idx" not in out:
        if not nums:
            raise ValueError("FRAME needs a time in seconds (or #<frame index>)")
        out["t"] = nums.pop(0)
    if len(nums) >= 4:
        out["box"] = nums[:4]
        nums = nums[4:]
    if nums and "scale" not in out:
        out["scale"] = nums[0]
    out.setdefault("scale", 1.0)
    return out


def parse_action(text: str, qids: list[int]) -> Action:
    """The FIRST action of a visible reply (python block, FRAME line or ANSWERS block)."""
    found: list[tuple[int, Action]] = []
    for m in _FENCE_PY.finditer(text or ""):
        body = m.group(2)
        lang = (m.group(1) or "").lower()
        if not lang and (body.lstrip().startswith("{") or _ANS.search(text[max(0, m.start() - 40):m.start()] or "")):
            continue                            # a bare fence holding the ANSWERS JSON
        if body.strip():
            found.append((m.start(), Action("python", body.strip("\n"))))
    for m in _FRAME.finditer(text or ""):
        try:
            found.append((m.start(), Action("frame", parse_frame_args(m.group(1)))))
        except ValueError as e:
            found.append((m.start(), Action("frame", None, error=str(e))))
    for m in _ANS.finditer(text or ""):
        rest = text[m.end():m.end() + 20]
        if "{" in rest or "```" in rest:
            found.append((m.start(), Action("answers", parse_answers(text[m.start():], qids))))
            break
    found = [f for f in found if not any(f[0] > s and f[0] < e for s, e in _fences(text) if f[1].kind != "python")]
    if not found:
        return Action("none")
    found.sort(key=lambda x: x[0])
    a = found[0][1]
    a.n_actions = len(found)
    return a


def _fences(text: str) -> list[tuple[int, int]]:
    """Spans of python code fences (FRAME / ANSWERS text inside code is not an action)."""
    return [(m.start(), m.end()) for m in _FENCE_PY.finditer(text or "") if (m.group(1) or "")]


# --------------------------------------------------------------------------- conversation

def _txt(s: str) -> dict:
    """a text item of a user message; the chat template joins items with nothing in between, so each text item
    carries its own line breaks (the template trims the message ends)"""
    return {"type": "text", "text": "\n" + str(s).strip("\n") + "\n"}


def _img_tokens(img) -> int:
    w, h = img.size
    return int(math.ceil(w / 32) * math.ceil(h / 32)) + 8


class Conversation:
    def __init__(self, clip: Clip, ws: Path, cfg: AgentConfig, deny: list[str]):
        self.clip, self.ws, self.cfg, self.deny = clip, ws, cfg, deny
        self.qids = clip.qids
        self.messages: list[dict] = [{"role": "system", "content": system_prompt(cfg)}]
        self.images: list = []
        self.turns: list[dict] = []
        self.state = "ready"                 # ready | tool | done
        self.steps = 0                       # actions executed or attempted
        self.malformed = 0
        self.failed = 0
        self.final_mode = False
        self.forced: str | None = None
        self.answers: dict[int, float] = {}
        self.sources: dict[int, str] = {}
        self.status = "running"
        self.t0: float | None = None
        self.active_s = 0.0                  # the clip's own time: its share of each generate() + its tool runs
        self._tool_dt = 0.0
        self.next_plain = False
        self.dropped_images = 0
        self.inputs: dict = {}
        self.pending: Action | None = None
        self.gen_tokens = 0

    # ---------------------------------------------------------------- setup
    def start(self) -> None:
        self.inputs = prepare_workspace(self.clip, self.ws)
        I = self.inputs
        dim = {"2": "2D", "3": "3D"}.get((self.clip.questions[0].get("video_type") or "  ")[1:2], "?")
        lines = [f"Video {self.clip.video_id}: {I['width']}x{I['height']} px, {I['n_frames']} frames, FPS {I['fps']:g} "
                 f"(dataset; container {I['container_fps']:.3g}), duration {I['duration_s']:.2f} s, video_source "
                 f"{self.clip.questions[0].get('video_source') or '?'}, video_type "
                 f"{self.clip.questions[0].get('video_type') or '?'} ({dim}).",
                 "Workspace (current directory): " + I["video_file"] + ", inputs.json, qptools.py.",
                 f"{len(self.clip.questions)} question(s); answer EVERY qid:"]
        for q in self.clip.questions:
            lines.append(f"- qid {q['qid']} [answer unit: {q['target_unit'] or 'as asked'}]: {q['question']}\n"
                         f"  prior: {q['prior']}" + (f"\n  depth_info: {q['depth_info']}" if q['depth_info'] else ""))
        content: list[dict] = [_txt("\n".join(lines))]
        try:
            sheet, idxs = contact_sheet(str(self.ws / I["video_file"]), I["fps"], I["n_frames"], self.cfg.frame_max_side)
            content += [_txt(f"Overview: frames {idxs} (2x2 sheet, reduced; use FRAME for measurements)."),
                        {"type": "image"}]
            self.images.append(sheet)
        except Exception as e:  # noqa: BLE001 - the clip still runs without an overview
            content.append(_txt(f"(overview not available: {e})"))
        content.append(_txt(f"Begin. You have {self.cfg.max_steps} actions."))
        self.messages.append({"role": "user", "content": content})
        self.turns.append({"role": "user", "text": "\n".join(c.get("text", "<image>") for c in content)})
        self.t0 = time.time()

    # ---------------------------------------------------------------- requests
    def est_tokens(self) -> int:
        n = 0
        for m in self.messages:
            c = m["content"]
            if isinstance(c, str):
                n += len(c)
            else:
                n += sum(len(x.get("text", "")) for x in c)
        return int(n / 3.0) + sum(_img_tokens(i) for i in self.images) + 16 * len(self.messages)

    def _max_tokens(self) -> int:
        if self.final_mode:
            return self.cfg.max_tokens_final
        return self.cfg.max_tokens_think if self.thinking_now() else self.cfg.max_tokens_plain

    def thinking_now(self) -> bool:
        return self.cfg.thinking and not self.final_mode and not self.next_plain

    def _drop_oldest_image(self) -> bool:
        for m in self.messages:
            if isinstance(m["content"], list):
                for k, x in enumerate(m["content"]):
                    if x.get("type") == "image":
                        m["content"][k] = _txt("[earlier image removed to save context]")
                        self.images.pop(0)
                        self.dropped_images += 1
                        return True
        return False

    def fit_context(self) -> None:
        if len(self.images) > self.cfg.max_images:
            while len(self.images) > self.cfg.keep_images and self._drop_oldest_image():
                pass
        budget = self.cfg.max_model_len - self._max_tokens() - 512
        while self.est_tokens() > budget and len(self.images) > 1 and self._drop_oldest_image():
            pass
        if self.est_tokens() > budget and not self.final_mode:
            self.force("the context is full")
            budget = self.cfg.max_model_len - self._max_tokens() - 512
        while self.est_tokens() > budget and self._drop_oldest_image():
            pass

    def request(self) -> CtxRequest:
        if not self.final_mode:
            if self.steps >= self.cfg.max_steps:
                self.force(f"the action budget ({self.cfg.max_steps}) is used up")
            elif self.active_s >= self.cfg.max_wall_s or (
                    self.t0 is not None and time.time() - self.t0 > self.cfg.max_elapsed_factor * self.cfg.max_wall_s):
                self.force(f"the time budget ({self.cfg.max_wall_s / 60:.0f} min) is used up")
        self.fit_context()
        think = self.thinking_now()
        samp = FINAL_SAMPLING if self.final_mode else (THINK_SAMPLING if think else PLAIN_SAMPLING)
        seed = (self.cfg.seed * 1000003 + sum(map(ord, self.clip.video_id)) * 97 + len(self.turns)) % (2**31)
        msgs = [dict(m, content=list(m["content"]) if isinstance(m["content"], list) else m["content"])
                for m in self.messages]                     # snapshot: the conversation keeps growing
        return CtxRequest(messages=msgs, images=list(self.images), max_tokens=self._max_tokens(),
                          temperature=samp["temperature"], top_p=samp["top_p"], top_k=samp["top_k"], seed=seed,
                          thinking=think)

    def force(self, reason: str) -> None:
        if self.final_mode:
            return
        self.final_mode = True
        self.forced = reason
        missing = [q for q in self.qids if q not in self.answers]
        self._user(FINAL_PROMPT.format(reason=reason, qids=", ".join(map(str, missing or self.qids))))

    def _user(self, text: str, images: list | None = None, captions: list[str] | None = None) -> None:
        """Append a user message (merged into the last message when that is a user message too)."""
        content: list[dict] = []
        for img, cap in zip(images or [], captions or []):
            content += [_txt(cap), {"type": "image"}]
            self.images.append(img)
        for cap in (captions or [])[len(images or []):]:
            content.append(_txt(cap))
        content.append(_txt(text))
        last = self.messages[-1]
        if last["role"] == "user" and isinstance(last["content"], list):
            last["content"].extend(content)
        else:
            self.messages.append({"role": "user", "content": content})
        self.turns.append({"role": "user", "text": text, "images": list(captions or [])})

    def _left(self) -> str:
        left = self.cfg.max_steps - self.steps
        tail = f"[{left} action(s) left, {max(0.0, self.cfg.max_wall_s - self.active_s) / 60:.1f} min left]"
        if left <= 3:
            tail += " Finish your measurements and send ANSWERS soon."
        return tail

    # ---------------------------------------------------------------- replies
    def on_reply(self, text: str | None) -> Action | None:
        """Consume one model reply. Returns the action to execute (python / frame) or None (state updated)."""
        if text is None:
            self.failed += 1
            self.turns.append({"role": "assistant", "text": None, "error": "generation failed"})
            if self.failed >= self.cfg.max_failed:
                self.finish("generation_failed")
            return None
        self.failed = 0
        think = self.thinking_now()
        thought, vis, ok = split_reply(text, think)
        self.gen_tokens += len(text) // 3
        rec = {"role": "assistant", "text": vis, "thinking_chars": len(thought),
               "thinking_tail": thought[-1500:] if thought else ""}
        if self.final_mode:
            got = parse_answers(vis or thought, self.qids, anywhere=True)
            rec["action"] = "final"
            self.turns.append(rec)
            self.messages.append({"role": "assistant", "content": vis or "(no reply)"})
            self._merge(got, "forced")
            self.finish("forced")
            return None
        if not ok:
            rec["action"] = "cut"
            self.turns.append(rec)
            self.messages.append({"role": "assistant", "content": "(reply cut off)"})
            self.steps += 1
            self.malformed += 1
            self.next_plain = True
            self._user(CUT_REPLY + " " + self._left())
            if self.malformed >= self.cfg.max_malformed:
                self.force("too many replies without an action")
            return None
        self.next_plain = False
        self.messages.append({"role": "assistant", "content": vis})
        act = parse_action(vis, self.qids)
        rec["action"] = act.kind
        self.turns.append(rec)
        if act.kind == "none":
            self.steps += 1
            self.malformed += 1
            if self.malformed >= self.cfg.max_malformed:
                self.force("too many replies without an action")
            else:
                self._user(NO_ACTION + " " + self._left())
            return None
        self.malformed = 0
        self.steps += 1
        note = " (Only the first action of your reply was executed: one action per reply.)" if act.n_actions > 1 else ""
        if act.kind == "answers":
            got = act.payload or {}
            self._merge(got, "agent")
            missing = [q for q in self.qids if q not in self.answers]
            if not missing:
                self.finish("done")
            elif self.steps >= self.cfg.max_steps:
                self.force(f"the action budget is used up and qid(s) {missing} have no valid answer")
            else:
                self._user(f"ANSWERS received but qid(s) {missing} have no valid positive number. Send a complete "
                           f"ANSWERS block for every qid ({', '.join(map(str, self.qids))}).{note} " + self._left())
            return None
        if act.kind == "frame" and act.payload is None:
            self._user(f"FRAME not understood: {act.error}. Example: FRAME 1.5 400 200 800 500 3{note} " + self._left())
            return None
        act.error = note
        self.state = "tool"
        self.pending = act
        return act

    def execute(self, act: Action) -> tuple[str, list, list[str]]:
        """Run one action (in a worker thread; its duration counts toward the clip's time). Never raises."""
        t0 = time.time()
        try:
            return self._execute(act)
        finally:
            self._tool_dt = time.time() - t0

    def _execute(self, act: Action) -> tuple[str, list, list[str]]:
        try:
            if act.kind == "python":
                txt, imgs, caps = run_python(act.payload, self.ws, self.steps, self.cfg.py_timeout, self.cfg.obs_chars,
                                             self.deny, self.cfg.mem_mb, show_max=self.cfg.show_per_run,
                                             max_side=self.cfg.frame_max_side)
                mb = dir_mb(self.ws, skip=self.inputs.get("video_file", ""))
                if mb > self.cfg.ws_warn_mb:
                    txt += f"\nWARNING: your workspace holds {mb:.0f} MB of files; delete large scratch files."
                return txt, imgs, caps
            p = act.payload
            img, cap = render_frame(str(self.ws / self.inputs["video_file"]), self.inputs["fps"],
                                    self.inputs["n_frames"], t=p.get("t"), idx=p.get("idx"), box=p.get("box"),
                                    scale=p.get("scale", 1.0), draw_grid=p.get("grid", True),
                                    max_side=self.cfg.frame_max_side)
            return "FRAME shown above.", [img], [cap]
        except Exception as e:  # noqa: BLE001 - reported to the model, the clip goes on
            return f"{act.kind} failed: {type(e).__name__}: {str(e)[:500]}", [], []

    def on_observation(self, obs: tuple[str, list, list[str]]) -> None:
        txt, imgs, caps = obs
        self.active_s += self._tool_dt
        self._tool_dt = 0.0
        note = self.pending.error if self.pending else ""
        self.pending = None
        self.state = "ready"
        self._user(f"{txt}{note}\n{self._left()}", imgs, caps)

    def _merge(self, got: dict[int, float], src: str) -> None:
        for q, v in got.items():
            if q in self.qids:
                self.answers[q] = float(v)
                self.sources[q] = src

    def _answers_file(self) -> dict[int, float]:
        """answers.json the model may have written in its workspace (used for qids still missing)."""
        f = self.ws / "answers.json"
        if not f.exists():
            return {}
        try:
            return answers_from_obj(json.loads(f.read_text()), self.qids)
        except (ValueError, OSError):
            return {}

    def finish(self, status: str) -> None:
        if self.state == "done":
            return
        extra = {q: v for q, v in self._answers_file().items() if q not in self.answers}
        self._merge(extra, "workspace_file")
        self.status = status
        self.state = "done"

    def record(self, model: str) -> tuple[dict, dict]:
        el = time.time() - (self.t0 or time.time())
        ans = {"video_id": self.clip.video_id, "status": "done", "end": self.status, "forced": self.forced,
               "answers": {str(q): self.answers[q] for q in self.qids if q in self.answers},
               "source": {str(q): self.sources[q] for q in self.qids if q in self.answers},
               "missing": [q for q in self.qids if q not in self.answers], "qids": self.qids,
               "reuse": {str(k): list(v) for k, v in self.clip.reuse.items()},
               "n_steps": self.steps, "wall_s": round(el, 1), "active_s": round(self.active_s, 1),
               "dropped_images": self.dropped_images,
               "model": model, "prompt_version": PROMPT_VERSION}
        tr = {"video_id": self.clip.video_id, "model": model, "prompt_version": PROMPT_VERSION,
              "config": asdict(self.cfg), "inputs": self.inputs, "turns": self.turns, "end": self.status,
              "forced": self.forced}
        return ans, tr


# --------------------------------------------------------------------------- scheduler

def save_json(path: Path, obj, indent: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, indent=indent, default=str))
    os.replace(tmp, path)


def load_answers(out: Path) -> dict[str, dict]:
    res = {}
    for p in sorted((out / "answers").glob("*.json")) if (out / "answers").exists() else []:
        try:
            rec = json.loads(p.read_text())
        except ValueError:
            continue
        if isinstance(rec, dict) and rec.get("status") == "done" and rec.get("video_id"):
            res[str(rec["video_id"])] = rec
    return res


def charge_generation(convs: list, replies: list, dt: float) -> None:
    """Charge each conversation its own share of a batched generate() call: decoding advances all sequences together,
    so a reply of k tokens finished after about k / k_max of the call (prefill ignored). This is roughly the time the
    clip would have taken alone, so the per-clip time cap does not depend on how many clips share the GPU."""
    lens = [len(r) if isinstance(r, str) else 0 for r in replies]
    top = max(lens) if lens and max(lens) > 0 else 1
    for c, n in zip(convs, lens):
        c.active_s += dt * max(n, 1) / top


def run_clips(backend, clips: list[Clip], out: Path, cfg: AgentConfig, ws_root: Path, model: str = "",
              concurrency: int = 32, tool_workers: int = 8, deadline: float | None = None, gather_s: float = 3.0,
              keep_ws: bool = False, deny: list[str] | None = None, log_every: int = 8) -> dict:
    """Run every clip that has questions and no finished answers file. Returns counters."""
    out = Path(out)
    done = load_answers(out)
    todo = deque(c for c in clips if c.questions and c.video_id not in done)
    deny = list(deny or [])
    for d in (str(ws_root), str(out)):
        if d not in deny:
            deny.append(d)
    active: list[Conversation] = []
    pending: dict = {}
    stats = {"clips": len(todo), "finished": 0, "forced": 0, "answered": 0, "questions": 0, "steps": 0,
             "gen_calls": 0, "gen_requests": 0, "skipped_deadline": 0}
    t_start = time.time()
    print(f"agent: {len(todo)} clip(s) to run, {sum(1 for c in clips if c.video_id in done)} already done, "
          f"{sum(1 for c in clips if not c.questions)} fully answered by their twin", flush=True)

    def gen(reqs):
        try:
            return list(backend.generate(reqs))
        except Exception as e:  # noqa: BLE001 - the batch is retried one by one
            print(f"  generate failed for {len(reqs)} requests ({type(e).__name__}: {str(e)[:300]}); one by one",
                  flush=True)
            res = []
            for r in reqs:
                try:
                    res.append(backend.generate([r])[0])
                except Exception:  # noqa: BLE001
                    res.append(None)
            return res

    def finalize(c: Conversation):
        ans, tr = c.record(model)
        save_json(out / "transcripts" / f"{safe_id(c.clip.video_id)}.json", tr)
        save_json(out / "answers" / f"{safe_id(c.clip.video_id)}.json", ans, indent=1)
        if not keep_ws:
            shutil.rmtree(c.ws, ignore_errors=True)
        stats["finished"] += 1
        stats["forced"] += int(c.forced is not None)
        stats["answered"] += len(ans["answers"])
        stats["questions"] += len(c.qids)
        stats["steps"] += c.steps
        if stats["finished"] % log_every == 0 or (not todo and not active):
            el = time.time() - t_start
            print(f"  agent {stats['finished']}/{stats['clips']} clips: {stats['answered']}/{stats['questions']} "
                  f"questions answered, {stats['forced']} forced, {stats['steps'] / stats['finished']:.1f} steps/clip, "
                  f"{el / 60:.1f} min ({el / stats['finished']:.0f} s/clip)", flush=True)

    with ThreadPoolExecutor(max_workers=max(1, tool_workers)) as pool:
        while todo or active:
            late = deadline is not None and time.time() > deadline
            while not late and todo and len(active) < concurrency:
                clip = todo.popleft()
                c = Conversation(clip, Path(ws_root) / safe_id(clip.video_id), cfg, deny)
                try:
                    c.start()
                except Exception as e:  # noqa: BLE001 - unreadable video: no answers file, retried next run
                    print(f"  {clip.video_id}: workspace not prepared ({type(e).__name__}: {e})", flush=True)
                    shutil.rmtree(c.ws, ignore_errors=True)
                    continue
                active.append(c)
            if late and todo:
                stats["skipped_deadline"] += len(todo)
                print(f"  deadline reached: {len(todo)} clip(s) not started (run again to continue)", flush=True)
                todo.clear()
            ready = [c for c in active if c.state == "ready"]
            if late:
                for c in ready:
                    c.force("the run's time budget is used up")
            if ready:
                reqs = [c.request() for c in ready]
                stats["gen_calls"] += 1
                stats["gen_requests"] += len(reqs)
                tg = time.time()
                replies = gen(reqs)
                charge_generation(ready, replies, time.time() - tg)
                for c, r in zip(ready, replies):
                    act = c.on_reply(r)
                    if act is not None:
                        pending[pool.submit(c.execute, act)] = c
            for c in [c for c in active if c.state == "done"]:
                finalize(c)
                active.remove(c)
            if pending:
                any_ready = any(c.state == "ready" for c in active)
                if any_ready:
                    fin, _ = wait(list(pending), timeout=0)
                else:   # gather: wait for the first tool, then briefly for more, so the next batch is larger
                    fin, _ = wait(list(pending), return_when=FIRST_COMPLETED)
                    more, _ = wait([f for f in pending if f not in fin], timeout=gather_s)
                    fin = set(fin) | set(more)
                for f in fin:
                    c = pending.pop(f)
                    c.on_observation(f.result())
    stats["wall_s"] = round(time.time() - t_start, 1)
    return stats


def fill_twins(clips: list[Clip], out: Path, model: str = "") -> int:
    """Write / complete the answers of segmented twins from their original's answers (Clip.reuse)."""
    have = load_answers(out)
    n = 0
    for c in clips:
        if not c.reuse:
            continue
        rec = have.get(c.video_id)
        if rec is None and c.questions:
            continue                     # twin's own questions not run yet: filled after its run
        rec = dict(rec) if rec else {"video_id": c.video_id, "status": "done", "end": "twin", "forced": None,
                                     "answers": {}, "source": {}, "missing": [], "qids": [], "n_steps": 0,
                                     "wall_s": 0.0, "model": model, "prompt_version": PROMPT_VERSION}
        ans, src = dict(rec.get("answers", {})), dict(rec.get("source", {}))
        changed = False
        for q, (ov, oq) in c.reuse.items():
            o = have.get(ov)
            v = (o or {}).get("answers", {}).get(str(oq))
            if v is not None and ans.get(str(q)) != v:
                ans[str(q)], src[str(q)] = v, f"twin:{ov}:{oq}"
                changed = True
        if not changed and c.video_id in have:
            continue
        qids = sorted(set(map(int, rec.get("qids", []))) | set(c.reuse))
        rec.update(answers=ans, source=src, qids=qids, missing=[q for q in qids if str(q) not in ans],
                   reuse={str(k): list(v) for k, v in c.reuse.items()})
        save_json(out / "answers" / f"{safe_id(c.video_id)}.json", rec, indent=1)
        n += 1
    return n


def write_csvs(df, out: Path, fallback: dict[int, float] | None = None) -> tuple[Path, Path]:
    """agent.csv (agent answers only; NaN where none) and agent_filled.csv (fallback where none), both with columns
    id, parsed_value, video_id, source (the format of the other direct.csv files: first column = qid)."""
    import pandas as pd
    have = load_answers(out)
    val, src = {}, {}
    for v, rec in have.items():
        for q, x in rec.get("answers", {}).items():
            val[int(q)] = float(x)
            src[int(q)] = rec.get("source", {}).get(q, "agent")
    ids = df.qid.astype(int).tolist()
    a = pd.DataFrame({"id": ids, "parsed_value": [val.get(q, math.nan) for q in ids],
                      "video_id": df.video_id.tolist(), "source": [src.get(q, "") for q in ids]})
    p1, p2 = out / "agent.csv", out / "agent_filled.csv"
    a.to_csv(p1, index=False)
    fb = fallback or {}
    b = a.copy()
    miss = b.parsed_value.isna()
    b.loc[miss, "parsed_value"] = [fb.get(q, math.nan) for q in b.id[miss]]
    b.loc[miss & b.parsed_value.notna(), "source"] = "fallback"
    b.to_csv(p2, index=False)
    print(f"wrote {p1} ({int(a.parsed_value.notna().sum())}/{len(a)} answered by the agent) and {p2} "
          f"({int(b.parsed_value.notna().sum())}/{len(b)} with the fallback)", flush=True)
    return p1, p2


def default_ws_root(split: str) -> Path:
    base = Path("/content") if Path("/content").is_dir() and os.access("/content", os.W_OK) else Path(tempfile.gettempdir())
    return base / "qp_agent_ws" / split
