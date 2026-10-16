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
    ANSWERS {"<qid>": <number>, ...}  final answers (positive magnitudes in the asked unit); ends the clip. The
                                      keyword (case-sensitive) starts a line (markdown decoration allowed) and is
                                      followed by the JSON object or a json / bare fence holding it.
The reply to an action is one user message: text (+ images for FRAME and for show() calls in Python).
Caps: steps (default 30), time per clip (default 8 min of the clip's OWN time: its share of each batched generate()
call + its tool runs, i.e. about what the clip would take alone; real elapsed time is capped at max_elapsed_factor x
that x max(1, concurrency / 8), factor 0 = no real-time cap), context budget (each prompt counted exactly with the
backend's tokenizer when it has count_tokens), consecutive malformed replies; on any cap the model gets one forced
"ANSWERS only" turn (no thinking, greedy). Answers are parsed leniently, made positive (abs), non-finite / zero values
dropped; qids still missing are left to the fallback (run_agent.py / build_sub.py).

Failures: a batch whose generate() raises is bisected so only the failing request(s) lose their reply and the rest
stay batched. A prompt over the context budget (pre-checked per request) or rejected by the engine as too long only
shrinks that conversation (old images, then old tool outputs dropped; else its final turn is forced); it never counts
as a failed generation and the same prompt is never sent again. After max_failed failed generations in a row a clip
gets one forced final turn, then ends with status "failed" (not "done": a re-run retries it). Several consecutive
rounds without any reply, or a dead engine (EngineDeadError), stop the run: finished clips are kept, the unfinished
ones are written as "failed" and BackendDead is raised (run_agent exits non-zero).

Scheduling: many clip conversations run at once. The loop gathers every conversation that waits for the model and
sends them to the backend in ONE generate() call (vLLM batches them), while tool calls (Python, frames) run in a
thread pool; before each generate() it waits up to tool_wait_s for running tools so a cohort is not split. A clip's
answers + transcript are written atomically when it finishes; finished clips are skipped on the next run (resumable).

Sandbox: every script runs in a fresh interpreter with a minimal environment (no tokens, no GPU, no pip index, 2
threads, nice +10, an address-space limit), behind a Python guard (no network, no reads of the deny roots). Run as
root (Colab), scripts also run as an unprivileged uid (65534) in their own network namespace, the workspace chowned to
that uid, and the deny roots (repo, Drive, outputs) closed to "other" users while the run lasts. Files the harness
reads back from a workspace are opened without following links. audit_transcript() lists suspicious accesses.

Backend contract: backend.generate(list[CtxRequest]) -> list[str | None] (None = failed generation); optional
backend.count_tokens(CtxRequest) -> int (exact prompt length including image tokens).
"""

from __future__ import annotations

import json
import math
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
from collections import deque
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, Callable

import cv2
import numpy as np

from qp.open.ctx_annot import CtxRequest, image_tokens
from qp.open.qwen_vl import _balanced, _loads

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = "Qwen/Qwen3.6-27B-FP8"
FALLBACK_MODEL = "Qwen/Qwen3.6-27B"
PROMPT_VERSION = "agent-v2"

# sampling (Qwen3.6 model card): thinking for precise tasks; non-thinking general; greedy for the forced final turn
THINK_SAMPLING = {"temperature": 0.6, "top_p": 0.95, "top_k": 20}
PLAIN_SAMPLING = {"temperature": 0.7, "top_p": 0.8, "top_k": 20}
FINAL_SAMPLING = {"temperature": 0.0, "top_p": 1.0, "top_k": -1}


@dataclass
class AgentConfig:
    max_steps: int = 30                 # actions per clip (the forced final turn comes on top)
    max_wall_s: float = 480.0           # time per clip: the clip's OWN model + tool time (see Conversation.active_s)
    max_elapsed_factor: float = 4.0     # real elapsed cap per clip = factor x max_wall_s x max(1, concurrency / 8);
    #                                     <= 0: no real-time cap (the own-time cap max_wall_s always applies)
    py_timeout: float = 60.0            # seconds per Python run
    obs_chars: int = 4096               # stdout + stderr returned per run (head + tail)
    thinking: bool = True               # reason before each action (cut replies retry the turn without)
    max_tokens_think: int = 4096
    max_tokens_plain: int = 3072
    max_tokens_final: int = 1536
    max_model_len: int = 65536          # context budget (must match the engine)
    ctx_margin: int = 512               # tokens kept free on top of max_tokens (template / count slack)
    max_images: int = 12                # images per prompt (engine limit_mm_per_prompt)
    keep_images: int = 8                # when over max_images, the oldest are dropped down to this many
    frame_max_side: int = 1280          # long side of every image sent
    show_per_run: int = 2               # images a Python run may attach with show()
    max_malformed: int = 4              # consecutive replies without an action -> forced final
    max_failed: int = 3                 # consecutive failed generations (None) -> one forced final turn, then "failed"
    mem_mb: int = 0                     # address-space limit of a Python run (0 = sandbox_mem_mb(tool_workers))
    ws_warn_mb: int = 300               # workspace size warning
    tool_wait_s: float = 15.0           # before each generate(): wait up to this long for running tools
    sandbox: str = "auto"               # "auto": as root, unprivileged uid + own network namespace; "off": guard only
    lock_deny: bool = True              # as root with an unprivileged sandbox: close the deny roots to "other" users
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

3. Final answers: on a line of its own, the word ANSWERS followed by one JSON object mapping EVERY qid to one \
positive number in the unit the question asks for (target_unit)
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
             "FRAME <t> [x0 y0 x1 y1] [scale] line, or a line starting with ANSWERS {...}.")
CUT_REPLY = ("Your reply was cut off before an action (too long). Keep the reasoning short and end with exactly one "
             "action.")
OBS_DROPPED = "[earlier output removed to save context]"
REPLY_DROPPED = "[earlier reply removed to save context]"
FAILED_ENDS = ("generation_failed", "error", "aborted")     # answers record status "failed": run again next time


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


def twin_key(q: dict) -> tuple[str, str, str, str]:
    """What must match for a segmented twin to reuse its original's answer: the normalised question, the exact prior
    and depth_info texts (whitespace aside: qp.postprocess.exact_text) and the asked unit."""
    from qp.postprocess import exact_text
    return (norm_question(q.get("question", "")), exact_text(q.get("prior")), exact_text(q.get("depth_info")),
            str(q.get("target_unit") or "").strip())


def plan_twins(clips: list[Clip]) -> list[Clip]:
    """Segmented twins (<video>_segmented, same footage with the background removed) reuse the original clip's answer
    to the same question (twin_key: normalised question, exact prior, exact depth_info, unit; as
    research/blind/build_agent_sub.py) when the original is in the same split: those questions are moved to
    Clip.reuse and not asked again (fill_twins records the source "twin:<orig>:<qid>"). Questions without a match run
    in the twin's own conversation. A twin with no question left keeps no questions (filled after the run)."""
    by_id = {c.video_id: c for c in clips}
    for c in clips:
        if not c.video_id.endswith("_segmented"):
            continue
        o = by_id.get(c.video_id[: -len("_segmented")])
        if o is None:
            continue
        omap: dict[tuple, int] = {}
        for q in o.questions:
            omap.setdefault(twin_key(q), int(q["qid"]))
        keep = []
        for q in c.questions:
            j = omap.get(twin_key(q))
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

GUARD = '''"""Sandbox guard, run by the boot code (not from a workspace file) before every script: limits,
thread caps, no network, no reads of the deny roots outside the workspace's allowed roots. Not a security boundary on
its own (as root the harness also runs scripts as an unprivileged uid in their own network namespace)."""
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

try:
    import cv2 as _cv2
    _cv2.setNumThreads(2)
    del _cv2
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


def _remove(p: Path) -> None:
    """Remove a file, link or directory tree (a symlink is removed itself, never followed)."""
    try:
        if os.path.islink(p) or not os.path.isdir(p):
            os.unlink(p)
        else:
            shutil.rmtree(p, ignore_errors=True)
    except FileNotFoundError:
        pass
    except OSError:
        shutil.rmtree(p, ignore_errors=True)


def _write_new(path: Path, text: str, mode: int = 0o644) -> None:
    """Create `path` afresh: whatever a script left there (a symlink to another file, say) is removed first and the
    file is created exclusively without following links, so the harness never writes through a planted link."""
    _remove(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), mode)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)


def _chown_tree(ws: Path, uid: int, gid: int) -> None:
    os.chown(ws, uid, gid)
    for root, dirs, files in os.walk(ws):
        for n in dirs + files:
            os.chown(os.path.join(root, n), uid, gid, follow_symlinks=False)


def prepare_workspace(clip: Clip, ws: Path, fps_fallback: float | None = None, owner: int | None = None) -> dict:
    """Fresh workspace: a COPY of the video (never a hard link: the workspace shares no inode with the dataset),
    inputs.json and qptools.py; chowned to `owner` (the sandbox uid) when given. Returns the inputs dict."""
    ws = Path(ws)
    if ws.exists() or ws.is_symlink():
        _remove(ws)
    ws.mkdir(parents=True)
    src = Path(clip.video_path)
    vf = "video" + (src.suffix or ".mp4")
    shutil.copy2(src, ws / vf)
    n, w, h, cfps = video_meta(str(ws / vf))
    fps = next((float(q["fps"]) for q in clip.questions if q.get("fps") and q["fps"] > 0), None) \
        or fps_fallback or cfps or 30.0
    inputs = {"video_id": clip.video_id, "video_file": vf, "width": w, "height": h, "n_frames": n, "fps": fps,
              "container_fps": cfps, "duration_s": n / fps, "questions": clip.questions}
    (ws / "inputs.json").write_text(json.dumps(inputs, indent=1))
    (ws / "qptools.py").write_text(QPTOOLS)
    if owner is not None:
        _chown_tree(ws, owner, owner)
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

NOBODY = 65534      # the unprivileged uid / gid scripts run as when the harness runs as root


@dataclass(frozen=True)
class SandboxPolicy:
    """How scripts are started. uid / gid: drop to these before the guard runs (only possible as root); netns:
    "os" = os.unshare(CLONE_NEWNET) in the child, "cmd" = the `unshare --net` command, "" = none (guard only)."""
    uid: int | None = None
    gid: int | None = None
    netns: str = ""
    nice: int = 10
    unshare: str = "unshare"
    notes: tuple = ()
    nproc: int = 2048           # with a uid change: RLIMIT_NPROC of the sandbox user (all its processes / threads)

    def describe(self) -> str:
        who = (f"uid {self.uid}/gid {self.gid}" if self.uid is not None
               else f"the current user (uid {os.geteuid()})")
        net = {"os": "own network namespace (os.unshare)", "cmd": "own network namespace (unshare --net)",
               "": "no network namespace (network blocked by the Python guard only)"}[self.netns]
        return f"scripts run as {who}, {net}, nice +{self.nice}" + ("; " + "; ".join(self.notes) if self.notes else "")


def sandbox_policy(euid: int, mode: str = "auto", have_os_unshare: bool = False, unshare_cmd: str | None = None,
                   uid: int = NOBODY) -> SandboxPolicy:
    """The sandbox decision (no side effects; resolve_sandbox probes the result): as root drop to `uid` and isolate
    the network (os.unshare when available, else the unshare command); not root, or mode "off": the current user
    and the Python guard only."""
    if mode == "off":
        return SandboxPolicy(notes=("sandbox hardening off: Python guard only",))
    if euid != 0:
        return SandboxPolicy(notes=("not running as root: no uid change, no network namespace",))
    netns = "os" if have_os_unshare else ("cmd" if unshare_cmd else "")
    notes = () if netns else ("neither os.unshare nor the unshare command is available: network blocked by the "
                              "Python guard only",)
    return SandboxPolicy(uid=uid, gid=uid, netns=netns, unshare=unshare_cmd or "unshare", notes=notes)


def _prelude(policy: SandboxPolicy) -> str:
    """First lines of every sandboxed interpreter: take the workspace (cwd) off sys.path, so no workspace module (a
    types.py, socket.py, resource.py, runpy.py the agent wrote) shadows what the prelude, the boot code or the guard
    import (_run_boot puts it back for the script); lower the priority, enter a new network namespace, drop root and
    cap the sandbox user's processes (a fork bomb)."""
    lines = ["import os, sys",
             "_qp_path0 = [p for p in sys.path if p in ('', '.') or p == os.getcwd()]",
             "sys.path[:] = [p for p in sys.path if p not in _qp_path0]"]
    if policy.nice:
        lines += ["try:", f"    os.nice({int(policy.nice)})", "except OSError:", "    pass"]
    if policy.netns == "os":
        lines.append("os.unshare(os.CLONE_NEWNET)")
    if policy.uid is not None:
        g = policy.gid if policy.gid is not None else policy.uid
        u = int(policy.uid)
        lines += ["os.setgroups([])", f"os.setgid({int(g)})", f"os.setuid({u})",
                  f"if os.getuid() != {u} or os.geteuid() != {u} or os.getgid() != {int(g)}:",
                  "    sys.exit('sandbox: privilege drop failed')"]
        if policy.nproc and policy.nproc > 0:
            n = int(policy.nproc)
            lines += ["try:", "    import resource as _r",
                      "    _h = _r.getrlimit(_r.RLIMIT_NPROC)[1]",
                      f"    _n = {n} if _h == _r.RLIM_INFINITY else min({n}, _h)",
                      "    _r.setrlimit(_r.RLIMIT_NPROC, (_n, _n))",
                      "    del _r, _h, _n",
                      "except (ImportError, OSError, ValueError):", "    pass"]
    return "\n".join(lines) + "\n"


def sandbox_argv(policy: SandboxPolicy, python: str, code: str) -> list[str]:
    """argv of one sandboxed interpreter running `code` after the prelude (-s: no user site-packages, whose
    usercustomize / .pth files would otherwise run before the privilege drop)."""
    argv = [python, "-s", "-c", _prelude(policy) + code]
    if policy.netns == "cmd":
        argv = [policy.unshare, "--net", "--"] + argv
    return argv


def _run_boot(script_name: str) -> str:
    """Boot code of a script run: the guard from this source (a workspace file could be edited by the agent), then the
    script as __main__. Everything the boot needs is imported while the workspace is off sys.path (see _prelude);
    the workspace goes back on sys.path just before the script runs (from qptools import *)."""
    return ("import types as _types\n"
            "_g = _types.ModuleType('_qp_guard')\n"
            f"exec(compile({GUARD!r}, '_qp_guard.py', 'exec'), _g.__dict__)\n"
            "sys.modules['_qp_guard'] = _g\n"
            "del _types, _g\n"
            "import runpy, pkgutil, warnings\n"
            "sys.path[:0] = globals().get('_qp_path0') or ['']\n"
            f"runpy.run_path({script_name!r}, run_name='__main__')\n")


def mem_available_mb() -> int | None:
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) // 1024
    except (OSError, ValueError, IndexError):
        pass
    return None


def sandbox_mem_mb(tool_workers: int, avail_mb: int | None = None, cap: int = 16384, reserve: int = 40000,
                   floor: int = 2048) -> int:
    """Address-space limit per sandbox: min(cap, (MemAvailable - reserve) // tool_workers) MB, at least `floor`
    (reserve: the engine process, vLLM workers and the page cache)."""
    if avail_mb is None:
        avail_mb = mem_available_mb()
    if avail_mb is None:
        return int(cap)
    return int(max(floor, min(cap, (int(avail_mb) - reserve) // max(1, int(tool_workers)))))


def sandbox_env(ws: Path, deny: list[str], mem_mb: int) -> dict:
    """A minimal environment: no tokens or API keys of the parent, no GPU, no package index, few threads."""
    import site
    allow = {sys.prefix, sys.base_prefix, sys.exec_prefix, *site.getsitepackages()}
    try:
        allow.add(site.getusersitepackages())
    except Exception:  # noqa: BLE001
        pass
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(ws), "LANG": "C.UTF-8",
           "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0", "PYTHONNOUSERSITE": "1", "MPLBACKEND": "Agg",
           "CUDA_VISIBLE_DEVICES": "", "OMP_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2", "MKL_NUM_THREADS": "2",
           "OPENCV_FOR_THREADS_NUM": "2", "OPENCV_FFMPEG_THREADS": "2", "OPENCV_LOG_LEVEL": "ERROR",
           "PIP_NO_INDEX": "1", "PIP_DISABLE_PIP_VERSION_CHECK": "1",
           "QP_MEM_MB": str(int(mem_mb)), "QP_ALLOW": os.pathsep.join(sorted(a for a in allow if a)),
           "QP_DENY": os.pathsep.join(deny), "TMPDIR": str(ws)}
    if os.environ.get("LD_LIBRARY_PATH"):
        env["LD_LIBRARY_PATH"] = os.environ["LD_LIBRARY_PATH"]
    return env


def _unreachable(path: Path, uid: int, gid: int) -> str | None:
    """The first directory on the way to `path` (itself included) that uid / gid cannot traverse, or None."""
    p = Path(os.path.realpath(path))
    for d in [*reversed(p.parents), p]:
        try:
            st = os.stat(d)
        except OSError:
            return str(d)
        if st.st_uid == uid:
            ok = st.st_mode & stat.S_IXUSR
        elif st.st_gid == gid:
            ok = st.st_mode & stat.S_IXGRP
        else:
            ok = st.st_mode & stat.S_IXOTH
        if not ok:
            return str(d)
    return None


_PROBE = r'''
import json, socket
r = {"uid": os.getuid(), "gid": os.getgid()}
try:
    r["ifaces"] = sorted(n for _, n in socket.if_nameindex())
except OSError:
    r["ifaces"] = None
import numpy, cv2
p = os.path.join(os.path.realpath(os.getcwd()), "_probe.txt")
with open(p, "w") as f:
    f.write("ok")
os.remove(p)
r["readable"] = [d for d in os.environ.get("QP_DENY", "").split(os.pathsep)
                 if d and os.path.exists(d) and os.access(d, os.R_OK | os.X_OK)]
print("QP_PROBE " + json.dumps(r))
'''


def probe_sandbox(policy: SandboxPolicy, root: Path, python: str | None = None,
                  deny: list[str] | tuple = ()) -> tuple[dict | None, str]:
    """Run a tiny script under `policy` in a scratch dir of `root` (the uid must reach the workspaces, import numpy
    and cv2, write its cwd; a network namespace must show only "lo"). (info, "") or (None, why it failed)."""
    try:
        d = Path(tempfile.mkdtemp(prefix="_qp_probe_", dir=str(root)))
    except OSError as e:
        return None, f"no scratch dir: {e}"
    try:
        if policy.uid is not None:
            os.chown(d, policy.uid, policy.gid if policy.gid is not None else policy.uid)
        r = subprocess.run(sandbox_argv(policy, python or sys.executable, _PROBE), cwd=str(d),
                           env=sandbox_env(d, list(deny), 0), stdin=subprocess.DEVNULL, capture_output=True,
                           text=True, timeout=120)
        line = next((x for x in reversed(r.stdout.splitlines()) if x.startswith("QP_PROBE ")), None)
        if r.returncode != 0 or line is None:
            return None, f"exit {r.returncode}: {(r.stderr or r.stdout).strip()[-300:]}"
        info = json.loads(line[len("QP_PROBE "):])
        if policy.uid is not None and info.get("uid") != policy.uid:
            return None, f"runs as uid {info.get('uid')}, not {policy.uid}"
        if policy.netns and info.get("ifaces") not in (["lo"], []):
            return None, f"network interfaces visible: {info.get('ifaces')}"
        return info, ""
    except Exception as e:  # noqa: BLE001 - any failure means: this policy does not work here
        return None, f"{type(e).__name__}: {str(e)[:300]}"
    finally:
        shutil.rmtree(d, ignore_errors=True)


_POLICIES: dict[tuple, SandboxPolicy] = {}


def _readable_deny(info: dict | None, ws_root: Path) -> list[str]:
    """deny roots the probe could read, except the workspace root and its ancestors (they must stay reachable)"""
    w = os.path.realpath(ws_root)
    return [d for d in (info or {}).get("readable") or []
            if not _inside(w, os.path.realpath(d)) and not _inside(os.path.realpath(d), w)]


def resolve_sandbox(root: Path, python: str | None = None, mode: str = "auto", deny: list[str] | tuple = (),
                    log: Callable[[str], Any] = print) -> SandboxPolicy:
    """The strongest sandbox that works here for workspaces under `root` (cached): sandbox_policy's decision, then a
    probe; when the probe fails it falls back (without the network namespace, without the uid change, guard only)
    with a logged warning."""
    py = python or sys.executable
    key = (py, os.path.realpath(root), mode)
    if key in _POLICIES:
        return _POLICIES[key]
    base = sandbox_policy(os.geteuid(), mode, hasattr(os, "unshare") and hasattr(os, "CLONE_NEWNET"),
                          shutil.which("unshare"))
    notes = list(base.notes)
    cands: list[SandboxPolicy] = []
    if base.uid is not None:
        bad = _unreachable(Path(root), base.uid, base.gid)
        if bad:
            notes.append(f"WARNING: {bad} cannot be traversed by uid {base.uid}, so scripts keep running as root "
                         f"(put the workspaces on a world-traversable path, e.g. --ws-root /content/agent_ws)")
        else:
            cands.append(base)
            if base.netns:
                cands.append(replace(base, netns=""))
    if base.netns:
        cands.append(replace(base, uid=None, gid=None))
    pol = replace(base, uid=None, gid=None, netns="")
    for c in cands:
        info, err = probe_sandbox(c, Path(root), py, deny)
        if info is not None:
            pol = c
            readable = _readable_deny(info, root)
            if readable:
                notes.append(f"the sandbox user can read {readable} until they are closed to other users "
                             f"(run_clips does so while it runs unless lock_deny is off; else only the Python guard "
                             f"blocks them)")
            break
        notes.append(f"WARNING: sandbox probe failed ({c.describe().split(';')[0]}): {err}")
    pol = replace(pol, notes=tuple(notes))
    log(f"sandbox: {pol.describe()}")
    _POLICIES[key] = pol
    return pol


def _sandbox_keep(ws_root: Path, python: str | None = None) -> list[str]:
    """Paths the sandbox user must keep reaching: the Python install and the workspaces."""
    import site
    keep = {sys.prefix, sys.base_prefix, sys.exec_prefix, os.path.dirname(os.path.realpath(python or sys.executable)),
            str(ws_root)}
    try:
        keep.update(site.getsitepackages())
    except Exception:  # noqa: BLE001
        pass
    return sorted({os.path.realpath(k) for k in keep if k})


def _inside(p: str, root: str) -> bool:
    return p == root or p.startswith(root.rstrip(os.sep) + os.sep)


def lock_deny_roots(deny: list[str], keep: list[str], log: Callable[[str], Any] = print) -> list[tuple[str, int]]:
    """While scripts run as the unprivileged uid: remove the "other" permission bits of every deny root (the repo
    with labels and Track A answers, Drive, the outputs) so the sandbox user cannot read them even past the Python
    guard. A deny root holding something the sandbox needs (`keep`: the Python install, the workspaces) is left as it
    is. Returns [(path, old mode)] for unlock_deny_roots."""
    locked = []
    for d in dict.fromkeys(deny):
        try:
            rp = os.path.realpath(d)
            if not os.path.isdir(rp) or any(_inside(k, rp) for k in keep):
                continue
            st = os.stat(rp)
            if not st.st_mode & 0o007:
                continue
            os.chmod(rp, stat.S_IMODE(st.st_mode) & ~0o007)
            locked.append((rp, stat.S_IMODE(st.st_mode)))
        except OSError as e:
            log(f"sandbox: WARNING: could not close {d} to other users ({e})")
    if locked:
        log(f"sandbox: closed to other users while the run lasts: {[p for p, _ in locked]}")
    return locked


def unlock_deny_roots(locked: list[tuple[str, int]], log: Callable[[str], Any] = print) -> None:
    for p, mode in locked:
        try:
            os.chmod(p, mode)
        except OSError as e:
            log(f"sandbox: WARNING: could not restore the mode of {p} ({e})")


def _killpg(pid: int) -> bool:
    try:
        os.killpg(pid, signal.SIGKILL)
        return True
    except (ProcessLookupError, PermissionError):
        return False


SANDBOX_ENV_MARKER = b"QP_DENY="        # in every sandbox environment (sandbox_env): marks the harness's processes


def clock_ticks_now(proc: str = "/proc") -> int | None:
    """The current time in clock ticks since boot (the unit of the starttime field of /proc/<pid>/stat), or None."""
    try:
        with open(os.path.join(proc, "uptime")) as f:
            return int(float(f.read().split()[0]) * os.sysconf("SC_CLK_TCK"))
    except (OSError, ValueError, IndexError, AttributeError):
        return None


def sandbox_pids(uid: int, since_ticks: int | None = None, proc: str = "/proc") -> list[int]:
    """Live processes left by sandboxed scripts: running as `uid` (real or effective) and started at or after
    `since_ticks` (/proc/<pid>/stat starttime) or carrying the sandbox environment. A script that calls setsid()
    escapes the process-group kill of run_python; other processes of that uid (a system daemon running as nobody,
    started before the run) are left alone. Zombies are skipped."""
    out: list[int] = []
    try:
        names = os.listdir(proc)
    except OSError:
        return out
    me = os.getpid()
    for n in names:
        if not n.isdigit() or int(n) == me:
            continue
        d = os.path.join(proc, n)
        try:
            with open(os.path.join(d, "status")) as f:
                ids = next((ln.split()[1:3] for ln in f if ln.startswith("Uid:")), [])
            if str(int(uid)) not in ids:
                continue
            with open(os.path.join(d, "stat")) as f:
                st = f.read()
            fields = st[st.rindex(")") + 1:].split()          # fields[0] = state (field 3), [19] = starttime
            if fields[0] in ("Z", "X"):
                continue
            ours = since_ticks is not None and int(fields[19]) >= since_ticks
            if not ours:
                with open(os.path.join(d, "environ"), "rb") as f:
                    ours = any(e.startswith(SANDBOX_ENV_MARKER) for e in f.read().split(b"\0"))
        except (OSError, ValueError, IndexError):
            continue
        if ours:
            out.append(int(n))
    return sorted(out)


def kill_sandbox_processes(uid: int, since_ticks: int | None = None, proc: str = "/proc",
                           log: Callable[[str], Any] = print) -> int:
    """SIGKILL every process sandbox_pids finds (a few passes: one may fork while the others are killed); run at the
    end of run_clips BEFORE the deny roots are opened again, so no script outlives the lock. Returns the count."""
    killed: set[int] = set()
    for _ in range(5):
        pids = [p for p in sandbox_pids(uid, since_ticks, proc) if p not in killed]
        if not pids:
            break
        for p in pids:
            try:
                os.kill(p, signal.SIGKILL)
                killed.add(p)
            except (ProcessLookupError, PermissionError):
                pass
        time.sleep(0.05)
    if killed:
        log(f"sandbox: killed {len(killed)} leftover process(es) of uid {uid} (scripts that left their session)")
    return len(killed)


def _truncate(text: str, n: int) -> str:
    if len(text) <= n:
        return text
    h = n // 2
    return text[:h] + f"\n... [{len(text) - 2 * h} characters omitted] ...\n" + text[-h:]


def _fsize(f) -> int:
    try:
        return os.fstat(f.fileno()).st_size
    except (OSError, ValueError):
        return 0


def _read_capped(f, n: int) -> str:
    """the file (an open binary file object) if it has at most n bytes, else its first and last n/2 bytes with the
    omitted count"""
    try:
        size = os.fstat(f.fileno()).st_size
        f.seek(0)
        if size <= n:
            return f.read(size).decode("utf-8", "replace")
        h = max(1, n // 2)
        head = f.read(h).decode("utf-8", "replace")
        f.seek(size - h)
        tail = f.read(h).decode("utf-8", "replace")
        return head + f"\n... [{size - 2 * h} bytes omitted] ...\n" + tail
    except (OSError, ValueError):
        return ""


_O_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
_O_DIRECTORY = getattr(os, "O_DIRECTORY", 0)
_O_NONBLOCK = getattr(os, "O_NONBLOCK", 0)


def _open_ws_dir(ws: Path, sub: str = "") -> int:
    fd = os.open(ws, os.O_RDONLY | _O_DIRECTORY | _O_NOFOLLOW)
    if not sub:
        return fd
    try:
        return os.open(sub, os.O_RDONLY | _O_DIRECTORY | _O_NOFOLLOW, dir_fd=fd)
    finally:
        os.close(fd)


def read_ws_bytes(ws: Path, rel: str, max_bytes: int) -> bytes | None:
    """Bytes of the regular file ws/rel (rel = "name" or "dir/name") or None. Never follows a symlink, refuses hard
    links, FIFOs and devices: the harness (maybe root) must not read other files through links a script planted."""
    parts = rel.split("/")
    try:
        dfd = _open_ws_dir(Path(ws), "/".join(parts[:-1]))
    except OSError:
        return None
    try:
        fd = os.open(parts[-1], os.O_RDONLY | _O_NOFOLLOW | _O_NONBLOCK, dir_fd=dfd)
    except OSError:
        os.close(dfd)
        return None
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or st.st_size > max_bytes:
            return None
        chunks, n = [], 0
        while n <= max_bytes:
            b = os.read(fd, min(1 << 20, max_bytes + 1 - n))
            if not b:
                break
            chunks.append(b)
            n += len(b)
        data = b"".join(chunks)
        return data if len(data) <= max_bytes else None
    except OSError:
        return None
    finally:
        os.close(fd)
        os.close(dfd)


def list_ws_dir(ws: Path, sub: str) -> list[str]:
    """Entries of the real directory ws/sub (not a symlink), or []."""
    try:
        fd = _open_ws_dir(Path(ws), sub)
    except OSError:
        return []
    try:
        return sorted(os.listdir(fd))
    except OSError:
        return []
    finally:
        os.close(fd)


def _ws_regular(p: Path) -> bool:
    """a regular file, not a symlink, not hard-linked elsewhere"""
    try:
        st = os.lstat(p)
    except OSError:
        return False
    return stat.S_ISREG(st.st_mode) and st.st_nlink == 1


_BOOT_TB = re.compile(r'  File "<string>", line \d+.*?(?=  File "_step)', re.S)


def run_python(code: str, ws: Path, step: int, timeout: float = 60.0, max_chars: int = 4096,
               deny: list[str] | None = None, mem_mb: int = 16384, python: str | None = None,
               show_max: int = 2, max_side: int = 1280,
               policy: SandboxPolicy | None = None) -> tuple[str, list, list[str]]:
    """Run `code` in a fresh interpreter with cwd = ws -> (observation text, images, image captions). policy None =
    resolve_sandbox(ws.parent) (cached). stdout / stderr go to unnamed temporary files of the harness (no path a
    script could swap); the whole process group is killed when the script ends (background children included)."""
    ws = Path(ws)
    py = python or sys.executable
    if policy is None:
        policy = resolve_sandbox(ws.parent, py)
    if policy.uid is not None:
        try:
            if os.stat(ws).st_uid != policy.uid:
                os.chown(ws, policy.uid, policy.gid if policy.gid is not None else policy.uid)
        except OSError:
            pass
    script = ws / f"_step{step:02d}.py"
    _write_new(script, code)
    show_dir = ws / "_show"
    _remove(show_dir)
    t0 = time.time()
    timed_out = False
    with tempfile.TemporaryFile() as fo, tempfile.TemporaryFile() as fe:
        proc = subprocess.Popen(sandbox_argv(policy, py, _run_boot(script.name)), cwd=str(ws), stdout=fo, stderr=fe,
                                stdin=subprocess.DEVNULL, env=sandbox_env(ws, deny or [], mem_mb),
                                start_new_session=True)
        try:
            rc = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            if not _killpg(proc.pid):
                proc.kill()
            rc = proc.wait()
        _killpg(proc.pid)                       # background children the script left behind (own session)
        dt = time.time() - t0
        n_out, n_err = _fsize(fo), _fsize(fe)
        err_budget = min(n_err, max_chars // 3) if n_out else min(n_err, max_chars)
        text = _read_capped(fo, max(256, max_chars - err_budget))
        se = _BOOT_TB.sub("", _read_capped(fe, max(256, max_chars - min(n_out, max_chars - err_budget))))
    head = (f"TIMEOUT after {timeout:g} s (process killed; make the script faster: fewer frames, smaller crops)"
            if timed_out else f"exit code {rc} ({dt:.1f} s)")
    parts = [f"Python result: {head}", "stdout:\n" + (text.rstrip() or "(empty)")]
    if se.strip():
        parts.append("stderr:\n" + se.rstrip())
    imgs, caps = [], []
    names = [n for n in list_ws_dir(ws, "_show") if n.endswith(".png")]
    for n in names[:show_max]:
        b = read_ws_bytes(ws, f"_show/{n}", 64 << 20)
        im = None
        if b:
            try:
                im = cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_UNCHANGED)
                if im is not None and im.dtype != np.uint8:
                    im = cv2.normalize(im, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
                if im is not None and im.ndim == 3 and im.shape[2] not in (3, 4):
                    im = None
            except Exception:  # noqa: BLE001 - an unreadable image is skipped
                im = None
        if im is None:
            caps.append(f"show() image {n[:-4]}: could not be read")
            continue
        lab = (read_ws_bytes(ws, f"_show/{n[:-4]}.txt", 4096) or b"").decode("utf-8", "replace").strip()[:200]
        try:
            imgs.append(_to_pil(im, max_side))
        except Exception:  # noqa: BLE001
            caps.append(f"show() image {n[:-4]}: could not be converted")
            continue
        caps.append(f"show() image {n[:-4]}: {lab or 'no label'} ({im.shape[1]}x{im.shape[0]} px"
                    f"{', shrunk to ' + str(max_side) + ' px' if max(im.shape[:2]) > max_side else ''})")
    if len(names) > show_max:
        caps.append(f"({len(names) - show_max} more show() images were not attached; max {show_max} per run)")
    _remove(show_dir)
    return "\n".join(parts), imgs, caps


def dir_mb(d: Path, skip: str = "") -> float:
    tot = 0
    for root, _, files in os.walk(d):
        for f in files:
            if f == skip:
                continue
            try:
                tot += os.lstat(os.path.join(root, f)).st_size
            except OSError:
                pass
    return tot / 2**20


# --------------------------------------------------------------------------- parsing

_THINK_CLOSE = "</think>"
_FENCE_MARK = re.compile(r"`{3,}")
_FENCE_TAG = re.compile(r"[ \t]*([A-Za-z0-9_+.#-]*)")
CODE_TAGS = ("python", "py", "python3", "")
_FRAME = re.compile(r"^[ \t>*`#_\-]*(?:[Aa]ction\s*:?[ \t*`_]*)?FRAME\b[ \t:]*(.*)$", re.M)
# ANSWERS (case-sensitive) at the start of a line (markdown decoration allowed: **ANSWERS**, > ANSWERS, ### ANSWERS:),
# followed by the JSON object or by a json / bare fence holding it
_ANS = re.compile(r"^[ \t>*_#`\-]*ANSWERS(?![A-Za-z0-9_])[*_`]*[ \t]*[:=]?[ \t]*[*_`]*\s*"
                  r"(?=\{|```[ \t]*(?:json5?|JSON)?[ \t]*\r?\n)", re.M)
_ANS_LOOSE = re.compile(r"\banswers?\b[*_`\s:=]*", re.I)        # forced final turn only
_NUMP = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
_NUM = re.compile(_NUMP)
_RANGE = re.compile(rf"(?:\b([xXyY])\s*[=:]?\s*)?({_NUMP})\s*(?:\.\.\.?|…|–|—|-|\bto\b)\s*({_NUMP})")


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


def _value(x, _depth: int = 0) -> float | None:
    """A positive finite number from a model value (number, numeric string with a unit, {"value": ..}, [x, ..]) or
    None. Never raises."""
    try:
        if _depth > 8 or isinstance(x, bool):
            return None
        if isinstance(x, dict):
            for k in ("value", "answer", "val", "estimate", "number"):
                if k in x:
                    return _value(x[k], _depth + 1)
            return None
        if isinstance(x, (list, tuple)):
            return _value(x[0], _depth + 1) if x else None
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
    except (OverflowError, ValueError, TypeError, RecursionError):
        return None


def _qid(k) -> int | None:
    try:
        if isinstance(k, bool):
            return None
        if isinstance(k, int):
            return k
        m = re.search(r"\d+", str(k))
        return int(m.group(0)) if m and len(m.group(0)) <= 12 else None
    except Exception:  # noqa: BLE001
        return None


def answers_from_obj(obj, qids: list[int]) -> dict[int, float]:
    want, out = set(qids), {}
    try:
        if isinstance(obj, dict) and isinstance(obj.get("answers"), (dict, list)):
            obj = obj["answers"]
        if isinstance(obj, dict):
            items = list(obj.items())
        elif isinstance(obj, list):
            items = [((o.get("qid") if isinstance(o, dict) else None), o) for o in obj]
        else:
            return out
        for k, x in items:
            q = _qid(k)
            v = _value(x)
            if q in want and v is not None:
                out[q] = v
    except Exception:  # noqa: BLE001 - whatever was parsed so far
        pass
    return out


def _json_after(text: str, start: int):
    """(the JSON object starting at the first "{" at or after `start`, its index) or (None, -1). Never raises."""
    try:
        i = text.find("{", start)
        if i < 0:
            return None, -1
        sub = _balanced(text, i)
        if sub is None:            # cut or unbalanced: try to close it
            sub = text[i:].split("```")[0].rstrip().rstrip(",") + "}"
        return _loads(sub), i
    except Exception:  # noqa: BLE001
        return None, -1


def parse_answers(text: str, qids: list[int], anywhere: bool = False) -> dict[int, float]:
    """Answers from an ANSWERS block (the keyword at a line start; lenient JSON: fenced, single quotes, int keys,
    trailing commas, unit strings, a list of {qid, answer} objects, a cut-off object). anywhere=True (forced final
    turn only): also "answers" anywhere in any case, then any JSON object, then "qid: number" pairs. Never raises."""
    if not text or not isinstance(text, str):
        return {}
    best: dict[int, float] = {}
    try:
        for m in list(_ANS.finditer(text))[:32]:          # each try scans to the end: a bound keeps it linear
            got = answers_from_obj(_json_after(text, m.end())[0], qids)
            if len(got) > len(best):
                best = got
        if best or not anywhere:
            return best
        for m in list(_ANS_LOOSE.finditer(text))[:32]:
            got = answers_from_obj(_json_after(text, m.end())[0], qids)
            if len(got) > len(best):
                best = got
        if best:
            return best
        for i in [i for i, c in enumerate(text) if c == "{"][:32]:
            sub = _balanced(text, i)
            got = answers_from_obj(_loads(sub) if sub else None, qids)
            if len(got) > len(best):
                best = got
        if not best:
            want = set(qids)
            for m in re.finditer(r"(?:qid\s*)?[\"']?(\d{1,12})[\"']?\s*[:=]\s*[\"']?"
                                 r"([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)", text):
                q, v = int(m.group(1)), _value(m.group(2))
                if q in want and v is not None and q not in best:
                    best[q] = v
    except Exception:  # noqa: BLE001 - whatever was found so far
        pass
    return best


def _floats(s: str) -> list[float]:
    vals = [float(x) for x in _NUM.findall(s)]
    if any(not math.isfinite(v) or abs(v) > 1e7 for v in vals):
        raise ValueError("FRAME numbers must be finite pixel coordinates / seconds")
    return vals


def parse_frame_args(s: str) -> dict:
    """'1.5', 't=1.5 100 200 300 400 2', '#37 box=[10,20,30,40] scale=3 nogrid', 't=1 x0=100 y0=80 x1=180 y1=160',
    '1.0 x 100..180, y 80..160 3' -> {t | idx, box, scale, grid}. Label prefixes (t=, x0=, y1:, box=) are stripped and
    a..b ranges read as (x range, y range) before the bare numbers are read."""
    s = str(s or "").strip().strip("`*_").strip()
    out: dict[str, Any] = {"grid": not re.search(r"\bno[ _-]?grid\b", s, re.I)}
    s = re.sub(r"\bno[ _-]?grid\b", " ", s, flags=re.I)

    def take(pat: str, flags=re.I):
        nonlocal s
        m = re.search(pat, s, flags)
        if m:
            s = s[:m.start()] + " " + s[m.end():]
        return m

    m = take(rf"\b(?:scale|zoom)\s*[=:]?\s*({_NUMP})")
    if m:
        out["scale"] = _floats(m.group(1))[0]
    m = take(r"(?:#\s*|\b(?:idx|index)\s*[=:]?\s*|\bframe\s*[=:]\s*)(\d{1,9})\b")
    if m:
        out["idx"] = int(m.group(1))
    m = take(rf"\b(?:t|time)\s*[=:]\s*({_NUMP})")
    if m:
        out["t"] = _floats(m.group(1))[0]
    elif re.search(r"\b(?:t|time)\s*[=:]", s, re.I):
        raise ValueError("FRAME t= needs a time in seconds")
    def cut_all(ms) -> None:
        nonlocal s
        for mm in sorted(ms, key=lambda mm: -mm.start()):
            s = s[:mm.start()] + " " + s[mm.end():]

    # 1. labelled corners x0= y0= x1= y1= (any order)
    ms = list(re.finditer(rf"\b([xy][01])\s*[=:]\s*({_NUMP})", s, re.I))
    lab = {mm.group(1).lower(): _floats(mm.group(2))[0] for mm in ms}
    if all(k in lab for k in ("x0", "y0", "x1", "y1")):
        out["box"] = [lab["x0"], lab["y0"], lab["x1"], lab["y1"]]
        cut_all(ms)
    # 2. ranges a..b (a-b, a to b): "x 100..180, y 80..160" or two bare ranges = (x range, y range)
    if "box" not in out:
        rng = list(_RANGE.finditer(s))
        if len(rng) >= 2:
            xr = next((r for r in rng if (r.group(1) or "").lower() == "x"), None)
            yr = next((r for r in rng if (r.group(1) or "").lower() == "y"), None)
            free = [r for r in rng if not r.group(1)]
            xr = xr or (free.pop(0) if free else None)
            yr = yr or (free.pop(0) if free else None)
            if xr is not None and yr is not None:
                (xa, xb), (ya, yb) = _floats(xr.group(2) + " " + xr.group(3)), _floats(yr.group(2) + " " + yr.group(3))
                out["box"] = [xa, ya, xb, yb]
                cut_all([xr, yr])
    # 3. labelled corner + size x= y= w= h=
    if "box" not in out:
        ms = list(re.finditer(rf"\b([xywh]|width|height)\s*[=:]\s*({_NUMP})", s, re.I))
        lab = {mm.group(1).lower()[:1]: _floats(mm.group(2))[0] for mm in ms}
        if all(k in lab for k in "xywh"):
            out["box"] = [lab["x"], lab["y"], lab["x"] + lab["w"], lab["y"] + lab["h"]]
            cut_all(ms)
    s = re.sub(r"\b[A-Za-z_]+\d?\b", " ", s)               # remaining labels / words (box, crop, at, x, y, ...)
    nums = _floats(s.replace(",", " "))
    if "t" in out and "box" not in out and len(nums) in (5, 6) and nums[0] == out["t"]:
        nums.pop(0)                                         # "FRAME 2 (t=2) x0 y0 x1 y1": the time written twice
    if "idx" not in out and "t" not in out:
        if not nums:
            raise ValueError("FRAME needs a time in seconds (or #<frame index>)")
        out["t"] = nums.pop(0)
    if "box" not in out and len(nums) >= 4:
        out["box"] = nums[:4]
        nums = nums[4:]
    if nums and "scale" not in out:
        out["scale"] = nums[0]
    out.setdefault("scale", 1.0)
    return out


def _fence_blocks(text: str) -> list[tuple[int, int, str, str]]:
    """(start, end, tag, body) of the fenced blocks of a reply. ``` markers are paired in order whatever their
    language tag, so a closing fence never opens a block; an unclosed last block runs to the end (a cut reply)."""
    marks = list(_FENCE_MARK.finditer(text))
    out, i = [], 0
    while i < len(marks):
        o = marks[i]
        t = _FENCE_TAG.match(text, o.end())
        tag, b0 = t.group(1).lower(), t.end()
        nl = text.find("\n", b0)
        line_end = len(text) if nl < 0 else nl
        if i + 1 < len(marks):
            end, b1 = marks[i + 1].end(), marks[i + 1].start()
            i += 2
        else:
            end, b1 = len(text), len(text)
            i += 1
        if b1 > line_end:                 # a block over lines: the body starts on the line after the opening fence
            b0 = line_end + 1
        out.append((o.start(), end, tag, text[b0:b1]))
    return out


def _is_code(tag: str, body: str) -> bool:
    """python / py / python3 / untagged blocks are code, except an untagged block holding JSON or an action line"""
    b = body.strip()
    if tag not in CODE_TAGS or not b:
        return False
    return not (tag == "" and (b[0] in "{[" or re.match(r"(?:ANSWERS|FRAME)\b", b)))


def parse_action(text: str, qids: list[int]) -> Action:
    """The FIRST action of a visible reply (python block, FRAME line or ANSWERS block). Never raises."""
    try:
        return _parse_action(text or "", qids)
    except Exception as e:  # noqa: BLE001 - a parser bug must not end the clip: treated as a reply without action
        return Action("none", error=f"{type(e).__name__}: {e}")


def _parse_action(text: str, qids: list[int]) -> Action:
    ans = list(_ANS.finditer(text))
    ans_fences = {m.end() for m in ans if text.startswith("```", m.end())}
    code = [(s, e, body) for s, e, tag, body in _fence_blocks(text) if s not in ans_fences and _is_code(tag, body)]

    def in_code(p: int) -> bool:
        return any(s < p < e for s, e, _ in code)

    found: list[tuple[int, Action]] = [(s, Action("python", body.strip("\n"))) for s, _, body in code]
    for m in _FRAME.finditer(text):
        if in_code(m.start()):
            continue
        try:
            found.append((m.start(), Action("frame", parse_frame_args(m.group(1)))))
        except Exception as e:  # noqa: BLE001 - reported to the model
            found.append((m.start(), Action("frame", None, error=str(e) or type(e).__name__)))
    for m in ans:
        if not in_code(m.start()):
            found.append((m.start(), Action("answers", parse_answers(text[m.start():], qids))))
            break
    if not found:
        return Action("none")
    found.sort(key=lambda x: x[0])
    a = found[0][1]
    a.n_actions = len(found)
    return a


# --------------------------------------------------------------------------- conversation

def _txt(s: str) -> dict:
    """a text item of a user message; the chat template joins items with nothing in between, so each text item
    carries its own line breaks (the template trims the message ends)"""
    return {"type": "text", "text": "\n" + str(s).strip("\n") + "\n"}


def _est_text_tokens(s: str) -> int:
    """Token estimate of text: digits 1 token each (Qwen tokenizers split numbers into digits), other text 3 chars."""
    s = str(s or "")
    d = sum(s.count(c) for c in "0123456789")
    return d + math.ceil((len(s) - d) / 3)


def estimate_tokens(req) -> int:
    """Prompt-length estimate of a request (used when the backend has no count_tokens)."""
    n = 0
    for m in req.messages:
        c = m["content"]
        n += 8 + (_est_text_tokens(c) if isinstance(c, str) else sum(_est_text_tokens(x.get("text", "")) for x in c))
    return n + sum(image_tokens(*im.size) + 4 for im in req.images)


class _TooLong:
    """Reply marker: the engine rejected this prompt as longer than its context (not a failed generation)."""
    __slots__ = ()

    def __repr__(self) -> str:
        return "TOO_LONG"


TOO_LONG = _TooLong()
TOO_LONG_STEP = 2048          # after an engine rejection the next prompt must count min(this, n / 8) tokens fewer


class Conversation:
    def __init__(self, clip: Clip, ws: Path, cfg: AgentConfig, deny: list[str], policy: SandboxPolicy | None = None):
        self.clip, self.ws, self.cfg, self.deny = clip, ws, cfg, deny
        self.policy = policy
        self.qids = clip.qids
        self.messages: list[dict] = [{"role": "system", "content": system_prompt(cfg)}]
        self.images: list = []
        self.turns: list[dict] = []
        self.state = "ready"                 # ready | tool | done
        self.steps = 0                       # actions executed or attempted
        self.malformed = 0
        self.failed = 0                      # consecutive failed generations
        self.failed_total = 0
        self.errors = 0                      # harness exceptions handled for this clip
        self.final_mode = False
        self.forced: str | None = None
        self.answers: dict[int, float] = {}
        self.sources: dict[int, str] = {}
        self.status = "running"
        self.t0: float | None = None
        self.active_s = 0.0                  # the clip's own time: its share of each generate() + its tool runs
        self.elapsed_cap_s: float | None = (cfg.max_elapsed_factor * cfg.max_wall_s
                                            if cfg.max_elapsed_factor > 0 else None)
        self._tool_dt = 0.0
        self.next_plain = False
        self.dropped_images = 0
        self.dropped_outputs = 0
        self.too_long = 0                    # prompts over the budget (pre-check) or rejected by the engine
        self.max_prompt: int | None = None   # after an engine rejection: later prompts must count fewer tokens
        self.last_prompt_tokens = 0
        self._n_start = 0                    # items of the first user message (the task) that are never dropped
        self._count_warned = False
        self.inputs: dict = {}
        self.pending: Action | None = None
        self.gen_tokens = 0

    # ---------------------------------------------------------------- setup
    def start(self) -> None:
        owner = self.policy.uid if self.policy is not None else None
        self.inputs = prepare_workspace(self.clip, self.ws, owner=owner)
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
        self._n_start = len(content)
        self.turns.append({"role": "user", "text": "\n".join(c.get("text", "<image>") for c in content)})
        self.t0 = time.time()

    # ---------------------------------------------------------------- requests
    def est_tokens(self) -> int:
        return estimate_tokens(self._build())

    def _max_tokens(self) -> int:
        if self.final_mode:
            return self.cfg.max_tokens_final
        return self.cfg.max_tokens_think if self.thinking_now() else self.cfg.max_tokens_plain

    def thinking_now(self) -> bool:
        return self.cfg.thinking and not self.final_mode and not self.next_plain

    def _budget(self) -> int:
        """the most prompt tokens this turn may have: the context minus max_tokens and the margin (and, after an
        engine rejection, below the rejected prompt)"""
        b = self.cfg.max_model_len - self._max_tokens() - self.cfg.ctx_margin
        return min(b, self.max_prompt) if self.max_prompt is not None else b

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

    def _old_outputs(self) -> list[tuple[int, int | None]]:
        """Droppable old text, oldest first: tool outputs (user text items; not the task, not the latest result
        before the final turn, never the latest instruction), then in the final turn old replies (not the last)."""
        users = [i for i, m in enumerate(self.messages) if m["role"] == "user"]
        asst = [i for i, m in enumerate(self.messages) if m["role"] == "assistant"]
        last_user, last_asst = (users[-1] if users else -1), (asst[-1] if asst else -1)
        obs, reps = [], []
        for i, m in enumerate(self.messages):
            c = m["content"]
            if m["role"] == "user" and isinstance(c, list):
                for k, x in enumerate(c):
                    t = x.get("text", "") if x.get("type") == "text" else ""
                    if len(t) <= 300 or OBS_DROPPED in t:
                        continue
                    if i == 1 and k < self._n_start:
                        continue
                    if i == last_user and (not self.final_mode or k == len(c) - 1):
                        continue
                    obs.append((i, k))
            elif m["role"] == "assistant" and self.final_mode and i != last_asst:
                if isinstance(c, str) and len(c) > 300 and c != REPLY_DROPPED:
                    reps.append((i, None))
        return obs + reps

    def _shrink(self, deficit: int) -> bool:
        """Drop old context worth about `deficit` tokens: the oldest images (one is kept until the final turn), then
        old tool outputs, then (final turn) old replies. False when nothing is left to drop."""
        saved, dropped = 0, False
        keep = 0 if self.final_mode else 1
        while saved < deficit and len(self.images) > keep:
            w, h = self.images[0].size
            if not self._drop_oldest_image():
                break
            saved += image_tokens(w, h)
            dropped = True
        for i, k in self._old_outputs():
            if saved >= deficit:
                break
            m = self.messages[i]
            if k is None:
                old, m["content"] = m["content"], REPLY_DROPPED
            else:
                old = m["content"][k]["text"]
                m["content"][k] = _txt(OBS_DROPPED)
            saved += max(1, _est_text_tokens(old) - _est_text_tokens(OBS_DROPPED))
            self.dropped_outputs += 1
            dropped = True
        return dropped

    def _count(self, req: CtxRequest, count: Callable | None) -> int:
        if count is not None:
            try:
                return int(count(req))
            except Exception as e:  # noqa: BLE001 - fall back to the estimate
                if not self._count_warned:
                    print(f"  {self.clip.video_id}: count_tokens failed ({type(e).__name__}: {str(e)[:200]}); "
                          f"using the estimate", flush=True)
                    self._count_warned = True
        return estimate_tokens(req)

    def _build(self) -> CtxRequest:
        think = self.thinking_now()
        samp = FINAL_SAMPLING if self.final_mode else (THINK_SAMPLING if think else PLAIN_SAMPLING)
        seed = (self.cfg.seed * 1000003 + sum(map(ord, self.clip.video_id)) * 97 + len(self.turns)) % (2**31)
        msgs = [dict(m, content=list(m["content"]) if isinstance(m["content"], list) else m["content"])
                for m in self.messages]                     # snapshot: the conversation keeps growing
        return CtxRequest(messages=msgs, images=list(self.images), max_tokens=self._max_tokens(),
                          temperature=samp["temperature"], top_p=samp["top_p"], top_k=samp["top_k"], seed=seed,
                          thinking=think, tag={"video_id": self.clip.video_id})

    def fit_context(self, count: Callable | None = None) -> CtxRequest | None:
        """The next request, shrunk to the context budget (prompt counted with `count`, else estimated): the image
        cap first, then old images / outputs, then the forced final turn, then (final turn) everything droppable.
        A prompt that still does not fit ends the clip ("too_long") without being sent: None."""
        if len(self.images) > self.cfg.max_images:
            while len(self.images) > self.cfg.keep_images and self._drop_oldest_image():
                pass
        n, over = 0, False
        for _ in range(500):
            req = self._build()
            n = self._count(req, count)
            if n <= self._budget():
                self.too_long += int(over)
                self.last_prompt_tokens = n
                req.tag["prompt_tokens"] = n
                return req
            over = True
            if self._shrink(n - self._budget()):
                continue
            if not self.final_mode:
                self.force("the context is full")
                continue
            break
        self.too_long += 1
        self.turns.append({"role": "system", "error": f"the prompt does not fit the context ({n} tokens, budget "
                                                      f"{self._budget()}) even after dropping old context"})
        self.finish("too_long")
        return None

    def request(self, count: Callable | None = None) -> CtxRequest | None:
        """The next model request (None when the clip ended instead: its prompt cannot fit the context)."""
        if self.state == "done":
            return None
        if not self.final_mode:
            if self.steps >= self.cfg.max_steps:
                self.force(f"the action budget ({self.cfg.max_steps}) is used up")
            elif self.active_s >= self.cfg.max_wall_s or (
                    self.elapsed_cap_s is not None and self.t0 is not None
                    and time.time() - self.t0 > self.elapsed_cap_s):
                self.force(f"the time budget ({self.cfg.max_wall_s / 60:.0f} min) is used up")
        return self.fit_context(count)

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
    def on_reply(self, text) -> Action | None:
        """Consume one model reply. Returns the action to execute (python / frame) or None (state updated).
        TOO_LONG: the engine rejected the prompt (the next one must be shorter; not a failed generation)."""
        if text is TOO_LONG:
            self.too_long += 1
            n = self.last_prompt_tokens or self.cfg.max_model_len
            cap = n if self.max_prompt is None else min(self.max_prompt, n)
            self.max_prompt = max(0, cap - min(TOO_LONG_STEP, max(256, n // 8)))
            self.turns.append({"role": "assistant", "text": None,
                               "error": f"prompt rejected as too long ({n} tokens counted); next prompt <= "
                                        f"{self.max_prompt} tokens"})
            return None
        if text is None:
            self.failed += 1
            self.failed_total += 1
            self.turns.append({"role": "assistant", "text": None, "error": "generation failed"})
            if self.failed >= self.cfg.max_failed:
                if self.final_mode:
                    self.finish("generation_failed")
                else:                        # one forced final turn before giving up on the clip
                    self.force(f"the model failed to reply {self.failed} times in a row")
            return None
        self.failed = 0
        text = str(text)
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

    def on_error(self, where: str, e: BaseException) -> None:
        """A harness exception while handling this clip's reply: logged in the transcript and treated as a reply
        without an action (the clip goes on)."""
        self.errors += 1
        self.turns.append({"role": "system", "error": f"{where}: {type(e).__name__}: {str(e)[:500]}"})
        if self.state == "done":
            return
        self.state, self.pending = "ready", None
        if self.final_mode:
            self.finish("error")
            return
        self.steps += 1
        self.malformed += 1
        if self.malformed >= self.cfg.max_malformed:
            self.force("too many replies without an action")
        else:
            self._user(f"Your last reply could not be processed ({type(e).__name__}). " + NO_ACTION + " "
                       + self._left())

    def crash(self, where: str, e: BaseException) -> None:
        """A harness exception that leaves this clip unusable: it ends with status "failed" (retried next run)."""
        self.errors += 1
        self.turns.append({"role": "system", "error": f"{where}: {type(e).__name__}: {str(e)[:500]}"})
        self.finish("error")

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
                                             self.deny, self.cfg.mem_mb or 16384, show_max=self.cfg.show_per_run,
                                             max_side=self.cfg.frame_max_side, policy=self.policy)
                mb = dir_mb(self.ws, skip=self.inputs.get("video_file", ""))
                if mb > self.cfg.ws_warn_mb:
                    txt += f"\nWARNING: your workspace holds {mb:.0f} MB of files; delete large scratch files."
                return txt, imgs, caps
            p = act.payload
            video = self.ws / self.inputs["video_file"]
            if not _ws_regular(video):
                raise ValueError(f"the workspace video {self.inputs['video_file']} was replaced or removed")
            img, cap = render_frame(str(video), self.inputs["fps"],
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
        """answers.json the model may have written in its workspace (used for qids still missing). Read without
        following links (a link to a label or answer file must not become an answer)."""
        b = read_ws_bytes(self.ws, "answers.json", 1 << 20)
        if not b:
            return {}
        try:
            return answers_from_obj(json.loads(b.decode("utf-8", "replace")), self.qids)
        except Exception:  # noqa: BLE001
            return {}

    def finish(self, status: str) -> None:
        if self.state == "done":
            return
        try:
            extra = {q: v for q, v in self._answers_file().items() if q not in self.answers}
            self._merge(extra, "workspace_file")
        finally:
            self.status = status
            self.state = "done"

    def record(self, model: str) -> tuple[dict, dict]:
        el = time.time() - (self.t0 or time.time())
        ans = {"video_id": self.clip.video_id, "status": "failed" if self.status in FAILED_ENDS else "done",
               "end": self.status, "forced": self.forced,
               "answers": {str(q): self.answers[q] for q in self.qids if q in self.answers},
               "source": {str(q): self.sources[q] for q in self.qids if q in self.answers},
               "missing": [q for q in self.qids if q not in self.answers], "qids": self.qids,
               "reuse": {str(k): list(v) for k, v in self.clip.reuse.items()},
               "n_steps": self.steps, "wall_s": round(el, 1), "active_s": round(self.active_s, 1),
               "dropped_images": self.dropped_images, "dropped_outputs": self.dropped_outputs,
               "too_long": self.too_long, "prompt_tokens": self.last_prompt_tokens,
               "failed_generations": self.failed_total, "errors": self.errors,
               "model": model, "prompt_version": PROMPT_VERSION}
        tr = {"video_id": self.clip.video_id, "model": model, "prompt_version": PROMPT_VERSION,
              "config": asdict(self.cfg), "inputs": self.inputs, "turns": self.turns, "end": self.status,
              "forced": self.forced}
        return ans, tr


# --------------------------------------------------------------------------- scheduler

class BackendDead(RuntimeError):
    """generate() keeps failing (a dead engine): the run stops. `stats` = the counters of the stopped run."""

    def __init__(self, msg: str, stats: dict | None = None):
        super().__init__(msg)
        self.stats = stats or {}


def _fatal_error(e: BaseException) -> bool:
    """An engine that cannot recover (vLLM v1 EngineDeadError)."""
    return type(e).__name__ == "EngineDeadError" or "EngineCore encountered an issue" in str(e)


def _too_long_error(e: BaseException) -> bool:
    """The engine's rejection of a prompt longer than its context (vLLM: '... is longer than the maximum model
    length of N')."""
    s = str(e).lower()
    return ("longer than the maximum model length" in s or "maximum context length" in s
            or ("too long" in s and ("prompt" in s or "context" in s)))


def save_json(path: Path, obj, indent: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, indent=indent, default=str))
    os.replace(tmp, path)


def load_answers(out: Path, statuses: tuple[str, ...] = ("done",)) -> dict[str, dict]:
    """answers/<clip>.json records by video_id with a status in `statuses` (default: finished clips only; a
    "failed" clip is not done, so the todo lists of run_agent and run_clips include it again). A record whose end is
    a failure (generation_failed / error / aborted) counts as "failed" whatever its status says (records of the first
    version wrote "done" for generation_failed clips)."""
    res = {}
    d = Path(out) / "answers"
    for p in sorted(d.glob("*.json")) if d.exists() else []:
        try:
            rec = json.loads(p.read_text())
        except (ValueError, OSError):
            continue
        if not isinstance(rec, dict) or not rec.get("video_id"):
            continue
        status = "failed" if rec.get("end") in FAILED_ENDS else rec.get("status")
        if status in statuses:
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


def elapsed_cap_s(cfg: AgentConfig, concurrency: int) -> float | None:
    """Real elapsed-time cap per clip: max_elapsed_factor x max_wall_s, scaled with the concurrency (a clip waits for
    the other clips' turns and tools); None (no cap) for a factor <= 0. The own-time cap max_wall_s always applies."""
    if cfg.max_elapsed_factor <= 0:
        return None
    return float(cfg.max_elapsed_factor * cfg.max_wall_s * max(1.0, concurrency / 8.0))


def run_clips(backend, clips: list[Clip], out: Path, cfg: AgentConfig, ws_root: Path, model: str = "",
              concurrency: int = 32, tool_workers: int = 8, deadline: float | None = None, gather_s: float = 3.0,
              keep_ws: bool = False, deny: list[str] | None = None, log_every: int = 8,
              max_dead_rounds: int = 3) -> dict:
    """Run every clip that has questions and no finished answers file. Returns counters. Raises BackendDead (with
    .stats) after max_dead_rounds consecutive rounds without any reply (from >= 2 clips) or on a dead engine: the
    finished clips are saved, the unfinished ones written as "failed" (run again next time)."""
    out, ws_root = Path(out), Path(ws_root)
    ws_root.mkdir(parents=True, exist_ok=True)
    if not cfg.mem_mb:
        cfg = replace(cfg, mem_mb=sandbox_mem_mb(tool_workers))
    done = load_answers(out)
    todo = deque(c for c in clips if c.questions and c.video_id not in done)
    deny = list(deny or [])
    for d in (str(ws_root), str(out)):
        if d not in deny:
            deny.append(d)
    active: list[Conversation] = []
    pending: dict = {}
    stats = {"clips": len(todo), "finished": 0, "failed": 0, "forced": 0, "answered": 0, "questions": 0, "steps": 0,
             "gen_calls": 0, "gen_requests": 0, "backend_calls": 0, "failed_requests": 0, "too_long": 0,
             "skipped_deadline": 0}
    t_start = time.time()
    count = getattr(backend, "count_tokens", None)
    count = count if callable(count) else None
    cap = elapsed_cap_s(cfg, concurrency)
    print(f"agent: {len(todo)} clip(s) to run, {sum(1 for c in clips if c.video_id in done)} already done, "
          f"{sum(1 for c in clips if not c.questions)} fully answered by their twin", flush=True)
    if not todo:
        stats["wall_s"] = 0.0
        return stats
    print(f"  prompts: {'counted with the backend tokenizer' if count else 'length estimated (no count_tokens)'}; "
          f"thinking turns max {cfg.max_tokens_think} tokens; per-clip caps {cfg.max_wall_s / 60:g} min own time, "
          f"{f'{cap / 60:.0f} min real time' if cap else 'no real-time cap'}; tools wait up to {cfg.tool_wait_s:g} s "
          f"before each batch; {tool_workers} tool worker(s), {cfg.mem_mb} MB per sandbox", flush=True)
    since_ticks = clock_ticks_now()
    since_ticks = None if since_ticks is None else since_ticks - 100     # 1 s of slack (/proc/uptime rounding)
    policy = resolve_sandbox(ws_root, mode=cfg.sandbox, deny=deny)
    locked: list = []

    def gen(reqs: list) -> list:
        """backend.generate with failure isolation: a batch that raises is bisected, so only the failing request(s)
        lose their reply (None, or TOO_LONG for a prompt the engine rejects as too long) and the rest stay batched."""
        def rec(rs: list) -> list:
            stats["backend_calls"] += 1
            try:
                res = list(backend.generate(rs))
                if len(res) != len(rs):
                    raise RuntimeError(f"backend returned {len(res)} replies for {len(rs)} requests")
                return res
            except Exception as e:  # noqa: BLE001
                if _fatal_error(e):
                    raise BackendDead(f"{type(e).__name__}: {str(e)[:300]}") from e
                msg = f"{type(e).__name__}: {str(e)[:300]}"
                if len(rs) == 1:
                    tl = _too_long_error(e)
                    vid = (getattr(rs[0], "tag", None) or {}).get("video_id", "?")
                    print(f"  generate failed for {vid} ({msg}) -> {'prompt too long' if tl else 'no reply'}",
                          flush=True)
                    stats["too_long" if tl else "failed_requests"] += 1
                    return [TOO_LONG if tl else None]
                print(f"  generate failed for {len(rs)} requests ({msg}); isolating the failing request(s)",
                      flush=True)
                h = len(rs) // 2
                return rec(rs[:h]) + rec(rs[h:])
        return rec(list(reqs))

    def crash(c: Conversation, where: str, e: BaseException) -> None:
        print(f"  {c.clip.video_id}: {where} failed ({type(e).__name__}: {str(e)[:300]}); clip ended", flush=True)
        try:
            c.crash(where, e)
        except Exception:  # noqa: BLE001
            c.state, c.status = "done", "error"

    def finalize(c: Conversation) -> None:
        try:
            ans, tr = c.record(model)
            save_json(out / "transcripts" / f"{safe_id(c.clip.video_id)}.json", tr)
            save_json(out / "answers" / f"{safe_id(c.clip.video_id)}.json", ans, indent=1)
        except Exception as e:  # noqa: BLE001 - not saved: the clip runs again next time
            print(f"  {c.clip.video_id}: result not saved ({type(e).__name__}: {str(e)[:300]})", flush=True)
            ans = {"answers": {}, "status": "failed"}
        if not keep_ws:
            shutil.rmtree(c.ws, ignore_errors=True)
        stats["finished"] += 1
        stats["failed"] += int(ans.get("status") != "done")
        stats["forced"] += int(c.forced is not None)
        stats["answered"] += len(ans["answers"])
        stats["questions"] += len(c.qids)
        stats["steps"] += c.steps
        if stats["finished"] % log_every == 0 or (not todo and not active):
            el = time.time() - t_start
            print(f"  agent {stats['finished']}/{stats['clips']} clips: {stats['answered']}/{stats['questions']} "
                  f"questions answered, {stats['forced']} forced, {stats['failed']} failed, "
                  f"{stats['steps'] / stats['finished']:.1f} steps/clip, "
                  f"{el / 60:.1f} min ({el / stats['finished']:.0f} s/clip)", flush=True)

    pool = ThreadPoolExecutor(max_workers=max(1, tool_workers))
    dead_rounds, dead_clips = 0, set()
    try:
        if policy.uid is not None and cfg.lock_deny:      # restored in the finally below
            locked = lock_deny_roots(deny, _sandbox_keep(ws_root))
            if locked:
                info, _ = probe_sandbox(policy, ws_root, None, deny)
                if _readable_deny(info, ws_root):
                    print(f"sandbox: WARNING: the sandbox user can still read {_readable_deny(info, ws_root)}",
                          flush=True)
        while todo or active:
            late = deadline is not None and time.time() > deadline
            while not late and todo and len(active) < concurrency:
                clip = todo.popleft()
                c = Conversation(clip, ws_root / safe_id(clip.video_id), cfg, deny, policy=policy)
                c.elapsed_cap_s = cap
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
                    try:
                        c.force("the run's time budget is used up")
                    except Exception as e:  # noqa: BLE001
                        crash(c, "force", e)
            batch = []
            for c in ready:
                if c.state != "ready":
                    continue
                try:
                    r = c.request(count)
                except Exception as e:  # noqa: BLE001 - this clip only
                    crash(c, "request", e)
                    continue
                if r is None or c.state != "ready":
                    continue
                if int((r.tag or {}).get("prompt_tokens", 0)) >= cfg.max_model_len:   # never send what must fail
                    stats["too_long"] += 1
                    c.on_reply(TOO_LONG)
                    continue
                batch.append((c, r))
            if batch:
                convs, reqs = [c for c, _ in batch], [r for _, r in batch]
                stats["gen_calls"] += 1
                stats["gen_requests"] += len(reqs)
                tg = time.time()
                replies = gen(reqs)
                charge_generation(convs, replies, time.time() - tg)
                if all(r is None for r in replies):
                    dead_rounds += 1
                    dead_clips.update(c.clip.video_id for c in convs)
                    if dead_rounds >= max_dead_rounds and len(dead_clips) >= 2:
                        raise BackendDead(f"{dead_rounds} consecutive generate() rounds without any reply "
                                          f"({len(dead_clips)} clips)")
                else:
                    dead_rounds, dead_clips = 0, set()
                for c, r in zip(convs, replies):
                    try:
                        act = c.on_reply(r)
                    except Exception as e:  # noqa: BLE001 - treated as a malformed reply of this clip
                        print(f"  {c.clip.video_id}: reply not processed ({type(e).__name__}: {str(e)[:300]})",
                              flush=True)
                        act = None
                        try:
                            c.on_error("reply", e)
                        except Exception as e2:  # noqa: BLE001
                            crash(c, "reply", e2)
                    if act is not None:
                        try:
                            pending[pool.submit(c.execute, act)] = c
                        except Exception as e:  # noqa: BLE001
                            crash(c, "tool submit", e)
            for c in [c for c in active if c.state == "done"]:
                finalize(c)
                active.remove(c)
            if pending:
                # wait for the running tools (all, or up to tool_wait_s) so the next batch keeps its cohort together
                fin, _ = wait(list(pending), timeout=max(0.0, cfg.tool_wait_s))
                if not fin and not any(c.state == "ready" for c in active):
                    fin, _ = wait(list(pending), return_when=FIRST_COMPLETED)
                    more, _ = wait([f for f in pending if f not in fin], timeout=gather_s)
                    fin = set(fin) | set(more)
                for f in fin:
                    c = pending.pop(f)
                    try:
                        obs = f.result()
                    except Exception as e:  # noqa: BLE001
                        obs = (f"tool failed: {type(e).__name__}: {str(e)[:500]}", [], [])
                    try:
                        c.on_observation(obs)
                    except Exception as e:  # noqa: BLE001
                        crash(c, "observation", e)
            elif not batch and active and not any(c.state == "ready" for c in active):
                for c in active:                        # a clip waiting for a tool that does not exist
                    if c.state != "done":
                        crash(c, "scheduler", RuntimeError(f"stuck in state {c.state!r}"))
    except BackendDead as e:
        print(f"  backend dead ({e}): no new clips; finished clips are saved, the {len(active)} unfinished clip(s) "
              f"are saved as failed and run again next time", flush=True)
        for f in list(pending):
            f.cancel()
        wait([f for f in pending if not f.cancelled()], timeout=cfg.py_timeout + 30)
        for c in list(active):
            if c.state != "done":
                try:
                    c.finish("aborted")
                except Exception:  # noqa: BLE001
                    c.state, c.status = "done", "aborted"
            finalize(c)
        active.clear()
        stats["aborted"] = str(e)[:500]
        stats["wall_s"] = round(time.time() - t_start, 1)
        e.stats = stats
        raise
    finally:
        pool.shutdown(wait=True, cancel_futures=True)
        if policy.uid is not None:      # no script of the sandbox user may outlive the lock (setsid() escapes killpg)
            try:
                kill_sandbox_processes(policy.uid, since_ticks)
            except Exception as e:  # noqa: BLE001
                print(f"sandbox: WARNING: leftover processes not killed ({type(e).__name__}: {e})", flush=True)
        unlock_deny_roots(locked)
    stats["wall_s"] = round(time.time() - t_start, 1)
    return stats


def fill_twins(clips: list[Clip], out: Path, model: str = "") -> int:
    """Write / complete the answers of segmented twins from their original's answers (Clip.reuse); the source of
    each reused answer is "twin:<original video>:<original qid>"."""
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


# --------------------------------------------------------------------------- transcript audit

AUDIT_PATTERNS = ("research/", "submissions/", "QuantiPhy-validation", "ground_truth", "/content/quantiphy",
                  "/content/drive", "../", "/proc/", "os.system", "subprocess", "os.popen", "ctypes", "os.symlink",
                  "os.link(", "socket.", "urllib", "/etc/", "setsid", "os.fork(", "/content/data_sync",
                  "/content/outputs_push")


def audit_transcript(path, patterns: tuple[str, ...] = AUDIT_PATTERNS, context: int = 80,
                     max_per_pattern: int = 3) -> list[dict]:
    """Suspicious accesses in one agent transcript (transcripts/<clip>.json or its dict): every turn text (the
    agent's replies and code, its thinking tail, the tool outputs, show() captions) that mentions a path or call a
    blind measurement has no business with (labels / Track A material, other repo folders, Drive, parent dirs,
    /proc, shells, subprocesses, links, sockets). [] = clean. Each hit: {"turn", "role", "field", "pattern",
    "snippet"} (case-insensitive match). An unreadable transcript is reported as one hit."""
    try:
        tr = path if isinstance(path, dict) else json.loads(Path(path).read_text())
        turns = tr.get("turns") or []
    except Exception as e:  # noqa: BLE001
        return [{"turn": None, "role": None, "field": None, "pattern": "<unreadable transcript>",
                 "snippet": f"{type(e).__name__}: {e}"[:300]}]
    hits = []
    for i, t in enumerate(turns):
        if not isinstance(t, dict):
            continue
        fields = [(f, t.get(f)) for f in ("text", "thinking_tail", "error")]
        if isinstance(t.get("images"), list):
            fields.append(("images", "\n".join(map(str, t["images"]))))
        for fld, s in fields:
            if not isinstance(s, str) or not s:
                continue
            low = s.lower()
            for p in patterns:
                pl, j, k = p.lower(), low.find(p.lower()), 0
                while j >= 0 and k < max_per_pattern:
                    hits.append({"turn": i, "role": t.get("role"), "field": fld, "pattern": p,
                                 "snippet": s[max(0, j - context):j + len(p) + context]})
                    j, k = low.find(pl, j + len(pl)), k + 1
    return hits


def audit_transcripts(out: Path, patterns: tuple[str, ...] = AUDIT_PATTERNS) -> dict[str, list[dict]]:
    """audit_transcript over <out>/transcripts/*.json -> {clip file stem: hits} for the clips with hits."""
    d = Path(out) / "transcripts"
    res = {}
    for p in sorted(d.glob("*.json")) if d.exists() else []:
        h = audit_transcript(p, patterns)
        if h:
            res[p.stem] = h
    return res


def default_ws_root(split: str) -> Path:
    base = Path("/content") if Path("/content").is_dir() and os.access("/content", os.W_OK) else Path(tempfile.gettempdir())
    return base / "qp_agent_ws" / split
