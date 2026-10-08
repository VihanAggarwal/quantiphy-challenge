"""Track A annotator: one Claude request per video -> QuestionSpec + pixel RoleTracks per question.

The request carries N uniform frames plus the frames nearest every time mentioned in the
video's questions / prior / depth text (t and t +/- delta), each labelled
"Frame <idx> (t=<sec>s)", at native resolution (Claude's coordinates map 1:1 to image pixels
up to 2576 px on the long edge). Claude answers with structured outputs (JSON schema), which
`to_annotations` converts into the shared contract of qp.spec (Obs.t = idx / dataset fps).

    params, meta = build_request(video_rows)       # rows of one video_id from qp.data.load_split
    msg = client.messages.create(**params)          # or a Message Batches request
    anns = to_annotations(json.loads(text), meta)   # {qid: Annotation}
"""

from __future__ import annotations

import base64
import json
import math
import re
from dataclasses import asdict, dataclass, field

import cv2
import numpy as np
import pandas as pd

from .frames import Frame
from .parse import _UNIT, _UNITS, canonical_unit
from .spec import KIND_DIM, KINDS, DepthEntry, Obs, Quantity, QuestionSpec, RoleTrack

MODEL = "claude-opus-5-5"
MAX_SIDE = 2576          # native-resolution limit; larger frames are downscaled and mapped back
ROLES = ("prior", "prior2", "target", "target2")
AXES = ("any", "horizontal", "vertical")

# --------------------------------------------------------------------------- output schema

_NUM_OR_NULL = {"anyOf": [{"type": "number"}, {"type": "null"}]}
_POINT = {"type": "array", "items": {"type": "number"}}
_QUANTITY = {
    "type": "object",
    "properties": {
        "kind": {"type": "string", "enum": list(KINDS)},
        "objects": {"type": "array", "items": {"type": "string"}},
        "dimension": {"type": "string"},
        "time": _NUM_OR_NULL,
        "window": {"anyOf": [{"type": "array", "items": {"type": "number"}}, {"type": "null"}]},
        "axis": {"type": "string", "enum": list(AXES)},
        "value_si": _NUM_OR_NULL,
        "unit": {"type": "string"},
    },
    "required": ["kind", "objects", "dimension", "time", "window", "axis", "value_si", "unit"],
    "additionalProperties": False,
}
_DEPTH = {
    "type": "object",
    "properties": {"object": {"type": "string"}, "distance_m": {"type": "number"}, "time": _NUM_OR_NULL},
    "required": ["object", "distance_m", "time"],
    "additionalProperties": False,
}
_OBS = {
    "type": "object",
    "properties": {
        "frame": {"type": "integer"},
        "point": {"anyOf": [_POINT, {"type": "null"}]},
        "extent": {"anyOf": [{"type": "array", "items": _POINT}, {"type": "null"}]},
        "box": {"anyOf": [_POINT, {"type": "null"}]},
    },
    "required": ["frame", "point", "extent", "box"],
    "additionalProperties": False,
}
_TRACK = {
    "type": "object",
    "properties": {"role": {"type": "string", "enum": list(ROLES)}, "object": {"type": "string"},
                   "obs": {"type": "array", "items": _OBS}},
    "required": ["role", "object", "obs"],
    "additionalProperties": False,
}
_QUESTION = {
    "type": "object",
    "properties": {
        "qid": {"type": "integer"},
        "spec": {
            "type": "object",
            "properties": {"target": _QUANTITY, "prior": _QUANTITY,
                           "depth": {"type": "array", "items": _DEPTH}, "notes": {"type": "string"}},
            "required": ["target", "prior", "depth", "notes"],
            "additionalProperties": False,
        },
        "tracks": {"type": "array", "items": _TRACK},
        "direct_answer": {"type": "number"},
        "confidence": {"type": "number"},
    },
    "required": ["qid", "spec", "tracks", "direct_answer", "confidence"],
    "additionalProperties": False,
}
# Structured outputs: every object lists all properties as required with additionalProperties
# false; nullable fields use anyOf [..., null]; no numeric / length / item-count constraints
# (unsupported), so shapes such as "point has 2 numbers" are validated in to_annotations.
SCHEMA = {
    "type": "object",
    "properties": {"questions": {"type": "array", "items": _QUESTION}},
    "required": ["questions"],
    "additionalProperties": False,
}
# Prompt v2: each track links its object to a depth_info entry (depth_name) or estimates its range
# (range_m, range_basis); each question carries a short derivation of the direct answer.
_TRACK_V2 = {
    "type": "object",
    "properties": {**_TRACK["properties"], "depth_name": {"type": "string"}, "range_m": _NUM_OR_NULL,
                   "range_basis": {"type": "string"}},
    "required": ["role", "object", "depth_name", "range_m", "range_basis", "obs"],
    "additionalProperties": False,
}
_QUESTION_V2 = {
    "type": "object",
    "properties": {**_QUESTION["properties"], "tracks": {"type": "array", "items": _TRACK_V2},
                   "derivation": {"type": "string"}},
    "required": ["qid", "spec", "tracks", "direct_answer", "confidence", "derivation"],
    "additionalProperties": False,
}
SCHEMA_V2 = {
    "type": "object",
    "properties": {"questions": {"type": "array", "items": _QUESTION_V2}},
    "required": ["questions"],
    "additionalProperties": False,
}
PROMPT_VERSIONS = ("v1", "v2")
LAB_FOV_DEG = 84.0    # horizontal FOV of the lab camera (video_source "lab": one rig, 854x480 val / 1280x720 test):
                      # GT-implied 76-90 deg on 6 val videos; stated to the model in v2, a prior on f in qp.geometry.
                      # A single-rig assumption (all lab 3D test clips are 1280x720) that val cannot check beyond
                      # those 6 scenes; qp.geometry.CAM_SIG_LOG_F sets how tightly it pins f

# --------------------------------------------------------------------------- prompt

SYSTEM = """\
You are a precise measurement annotator for QuantiPhy, a benchmark of quantitative physical \
reasoning from video. You see frames from ONE video. Each image is preceded by a label \
"Frame <idx> (t=<sec>s)": idx is the frame index in the original video and t = idx / fps is its \
time in seconds. All coordinates you give are pixels of the images as shown: x to the right, \
y down, origin at the top-left corner.

The video comes with one or more questions. Each question states one known physical quantity \
(the prior), may give object-to-camera distances (depth info, 3D videos only), and asks for \
another quantity (the target) in a stated unit. Every answer is (metric scale from the prior) x \
(a pixel measurement), so for every question you must:
1. parse it into a structured spec,
2. annotate pixel positions of the prior object and the target object(s) on the frames, so that a \
geometry program can compute the answer from your annotations, and
3. give your own best estimate of the answer, derived the same way.

Ground rules
- Measure on the frames and use the prior for scale. Never answer from world knowledge about \
typical sizes or speeds: many videos are simulations or staged scenes with unusual scales \
(a 20 m wide house next to a 1.2 m bird, a toy car moving at 0.6 m/s). The prior is exactly true \
for this video, even when it looks implausible.
- 2D videos: the motion happens roughly in a plane facing the camera, so one metres-per-pixel \
scale applies to the whole scene. 3D videos: the scale at an object is proportional to its \
camera distance (pinhole camera, metres per pixel = distance / focal length in pixels); use the \
depth info and annotate the objects on the frames at (or nearest to) the times the depth info \
refers to.
- Be precise: a few pixels matter on small objects. Give coordinates to 0.5 px.

Spec fields (for both "target" and "prior")
- kind: size (extent of one object: length, height, width, diameter, wingspan, thickness ...), \
distance (between two objects or two points, at one time), displacement (straight-line distance \
an object moves between two times), path_length (distance travelled along the path), speed \
(magnitude of velocity at a time, or averaged over a window), acceleration, camera_distance \
(object-to-camera distance, usually stated in the depth info), other.
- objects: short noun phrases naming the object(s), e.g. ["bird"]; two entries for a distance.
- dimension: for a size, the measured dimension ("length", "height", "width", "diameter", \
"wingspan", ...); otherwise "".
- time: the instant in seconds the quantity refers to ("at 1.5s", "t=1.5", "at time 1s"); \
"final"/"at the end" -> the time of the last frame; "initial"/"at the start" -> 0; null if not \
time-specific.
- window: [t0, t1] in seconds for averages, displacements or path lengths over a stated time \
range; null otherwise (null with time null means the whole clip).
- axis: "horizontal" or "vertical" when the question or prior says so (a gravity prior is \
vertical); otherwise "any".
- value_si: prior only - the known value converted to SI (m, m/s, m/s^2), e.g. 57.2mm -> 0.0572, \
7cm -> 0.07. null for the target.
- unit: target only - the unit the question asks for ("m", "cm", "mm", "m/s", "cm/s", "m/s^2", \
"cm/s^2", ...). "" for the prior.
- depth: one entry per line of the depth info: {object, distance_m, time (s, or null if no time \
is given)}; empty list for 2D videos.
- notes: short remarks on ambiguities or typos in the question; "" if none.

Tracks: one per role
- "prior": the object carrying the known quantity; "target": the object asked about; \
"target2": the second object of a distance between two objects; "prior2": the second object when \
the prior is a distance between two objects. When the prior and the target are the same object \
(e.g. "speed of the bird = 6 m/s; how long is the bird?") still give both tracks: the prior track \
with motion points, the target track with size extents.
- Each obs is one labelled frame: frame = its idx; point = [x, y]; extent = [[x1, y1], [x2, y2]]; \
box = [x1, y1, x2, y2] (tight bounding box). Use null for fields you do not give. Only use frame \
indices from the labels.
- Sizes (prior or target): give extent = the two endpoints of exactly the asked dimension \
(nose to tail for a length, wingtip to wingtip for a wingspan, top to bottom for a height, edge to \
edge through the centre for a diameter) plus the box, on 3-6 frames where the object is clearly \
visible and that dimension is fully shown (not foreshortened or occluded).
- Motion (speed, acceleration, displacement, path length): give point = one consistent reference \
point on the object (its centre, or one fixed feature - the same physical point in every frame) \
on every labelled frame where the object is visible, especially the frames around the asked \
times and window ends. Add the box where easy.
- Gravity priors ("gravity acc = 9.8 m/s^2"): the prior object is the object in free fall or \
projectile flight; give its point on every labelled frame while it is in flight (not after it \
lands or is caught). Use axis "vertical" for the prior.
- Distance between two objects: give point tracks for both (target and target2) on the frames at \
the asked time; use the points the distance is measured between (centres unless the question \
implies edges or a gap).
- camera_distance targets are read from the depth info; their tracks may be empty.
- To save output, a track for an object you already annotated earlier in this response may give \
the same object name (spelled identically) and an empty obs list; an earlier track of that object \
is then reused: the one with the most points for motion and distances, or one with extents of the \
same dimension for a size. A size of another dimension (e.g. the wingspan after the length) always \
needs its own extents.

Answer
- direct_answer: your best estimate of the target in the asked unit, computed from your own \
pixel measurements, the prior and (for 3D) the depth info. Always give a positive number.
- confidence: 0-1, how confident you are that direct_answer is within 10% of the truth.
Answer every question, in the order given, using its qid."""


SYSTEM_V2 = """\
You are a precise measurement annotator for QuantiPhy, a benchmark of quantitative physical \
reasoning from video. You see frames from ONE video. Each image is preceded by a label \
"Frame <idx> (t=<sec>s)": idx is the frame index in the original video and t = idx / fps is its \
time in seconds. All coordinates you give are pixels of the images as shown: x to the right, \
y down, origin at the top-left corner.

The video comes with one or more questions. Each question states one known physical quantity \
(the prior), may give object-to-camera distances (depth info, 3D videos only), and asks for \
another quantity (the target) in a stated unit. Every answer is (metric scale from the prior) x \
(a pixel measurement), so for every question you must:
1. parse it into a structured spec,
2. annotate pixel positions of the prior object and the target object(s) on the frames, so that a \
geometry program can compute the answer from your annotations, and
3. give your own best estimate of the answer, derived the same way.

Ground rules
- Measure on the frames and use the prior for scale. Never answer from world knowledge about \
typical sizes or speeds: many videos are simulations or staged scenes with unusual scales \
(a 20 m wide house next to a 1.2 m bird, a toy car moving at 0.6 m/s). The prior is exactly true \
for this video, even when it looks implausible.
- 2D videos: the motion happens roughly in a plane facing the camera, so one metres-per-pixel \
scale applies to the whole scene. 3D videos: the scale at an object is proportional to its \
camera distance (pinhole camera, metres per pixel = distance / focal length in pixels); the depth \
info gives the distance from the camera to the listed objects at the stated times. When the \
request states the camera's field of view, use that focal length.
- Be precise: a few pixels matter on small objects. Give coordinates to 0.5 px.

Spec fields (for both "target" and "prior")
- kind: size (extent of one object: length, height, width, diameter, wingspan, thickness ...), \
distance (between two objects or two points, at one time), displacement (straight-line distance \
an object moves between two times), path_length (distance travelled along the path), speed \
(magnitude of velocity at a time, or averaged over a window), acceleration, camera_distance \
(object-to-camera distance, usually stated in the depth info), other. A distance or height between \
an object and a surface or line (floor, ground, water, table top, wall, court line) is a \
"distance" with objects [object, surface].
- objects: short noun phrases naming the object(s), e.g. ["bird"]; two entries for a distance.
- dimension: for a size, the measured dimension ("length", "height", "width", "diameter", \
"wingspan", ...); otherwise "".
- time: the instant in seconds the quantity refers to ("at 1.5s", "t=1.5", "at time 1s"); \
"final"/"at the end" -> the time of the last frame; "initial"/"at the start" -> 0; null if not \
time-specific or when a window applies.
- window: [t0, t1] in seconds when the quantity holds over a time range: "from A to B" or \
"between A and B" -> [A, B]; "before T" -> [0, T]; "after T" -> [T, time of the last frame]; \
"in the first T seconds" -> [0, T]; "from T to the end" -> [T, time of the last frame]; null \
otherwise (null with time null means the whole clip).
- axis: "horizontal" or "vertical" when the question or prior says so (a gravity prior is \
vertical); otherwise "any".
- value_si: prior only - the known value converted to SI (m, m/s, m/s^2), e.g. 57.2mm -> 0.0572, \
7cm -> 0.07. null for the target.
- unit: target only - the unit the question asks for ("m", "cm", "mm", "m/s", "cm/s", "m/s^2", \
"cm/s^2", ...). "" for the prior.
- depth: leave it as an empty list: the program reads the depth info text itself.
- notes: short remarks on ambiguities or typos in the question; "" if none.

Tracks: one per role
- "prior": the object carrying the known quantity; "target": the object asked about; \
"target2": the second object (or the surface) of a distance; "prior2": the second object when \
the prior is a distance between two objects. When the prior and the target are the same object \
(e.g. "speed of the bird = 6 m/s; how long is the bird?") still give both tracks: the prior track \
with motion points, the target track with size extents.
- depth_name (3D videos): the object name exactly as written in the depth info (e.g. \
"distance_red_crate_camera" -> "red_crate") whose distance is this track's object, also \
when the question calls it differently ("the box" for "crate", "the kid" for "child"); "" \
when the depth info lists no distance for this object, and in 2D videos.
- range_m (3D videos): only when depth_name is "": your best estimate of the object's distance \
from the camera in metres at the annotated frames, from its relation to objects with known \
distance (standing next to a listed person, resting on the same shelf as a listed vase, crossing \
a listed object's position) or from its apparent size; null otherwise. range_basis: how you got \
range_m in one short sentence ("" when range_m is null).
- Each obs is one labelled frame: frame = its idx; point = [x, y]; extent = [[x1, y1], [x2, y2]]; \
box = [x1, y1, x2, y2] (tight bounding box). Use null for fields you do not give. Only use frame \
indices from the labels.
- Which object: resolve qualifiers (nearest, left, big, the one the depth info names) and use the \
same instance in every question of the video; in 3D prefer the instance whose apparent size and \
position fit its stated distance.
- Sizes (prior or target): extent = the two physical ends of exactly the asked dimension, plus the \
box. Height = a vertical physical line from the object's top to the point on its supporting \
surface directly below (in an elevated or oblique view the image-vertical extent of a car or box \
also contains its top surface: never use the box height). Length or width of an object seen at an \
angle = its two physical ends along that dimension (bumper to bumper, wheel contact to wheel \
contact), not the box diagonal. Wingspan = wingtip to wingtip; diameter = edge to edge through \
the centre, across the direction of motion. Measure on 3-6 frames where the object is sharp (not \
motion-blurred: blur stretches it along the motion), fully inside the image, unoccluded and \
closest to fronto-parallel, measuring each frame separately. The prior is the scale for \
everything: measure a size prior on at least 3 such frames (3D: at or next to the depth-info \
times). If no frame shows the dimension un-foreshortened, say so in notes.
- Sizes between parts listed in the depth info: when the depth info gives separate distances for \
the two ends or parts the asked size runs between (e.g. ramp_far and ramp_near for the ramp's \
length, shelf_left and shelf_right for the shelf's width), use kind "distance" with objects named \
exactly as in the depth info, and give point tracks for target (first part, depth_name set) and \
target2 (second part, depth_name set) at the physical points those entries refer to, on the \
same frames.
- Motion (speed, acceleration, displacement, path length): point = the centre of the object's \
tight box on that frame (ball centre, body centre), always with that box; never a top, bottom or \
edge point, which moves when the apparent size changes; a fixed feature only when the question \
names it (a racket head, a wheel hub). Give it on every labelled frame where the object is visible, \
especially the frames around the asked times and window ends. 3D videos: give the tight box on \
every labelled frame where the object is fully visible (not cut by the image border, not \
occluded): its apparent size tells how its camera distance changes between the depth-info times.
- Gravity priors ("gravity acc = 9.8 m/s^2"): the prior object is the object in free fall or \
projectile flight; give its point on every labelled frame while it is in flight (not after it \
lands or is caught). Use axis "vertical" for the prior.
- Distance between two objects: give point tracks for both (target and target2) on the SAME \
frames: the frame nearest the asked time and its neighbours; use the points the distance is \
measured between (centres unless the question implies edges or a gap; for "minimum", "closest" \
or "gap" the nearest points of the two objects). For an object and a surface, target2 is the \
point on the surface directly below the object (perpendicular for walls and lines). If an object \
is out of view at the asked time, give its positions on its last visible frames and say so in \
notes.
- camera_distance targets are read from the depth info; their tracks may be empty (set \
depth_name).
- To save output, a track for an object you already annotated earlier in this response may give \
the same object name (spelled identically) and an empty obs list; an earlier track of that object \
is then reused: the one with the most points for motion and distances, or one with extents of the \
same dimension for a size. A size of another dimension (e.g. the wingspan after the length) always \
needs its own extents.

Answer
- direct_answer: your best estimate of the target in the asked unit, computed from your own \
pixel measurements, the prior and (for 3D) the depth info. Always give a positive number.
- confidence: 0-1, how confident you are that direct_answer is within 10% of the truth.
- derivation: at most 200 characters: the pixel numbers and the scale or focal length you used, \
e.g. "prior 50 px = 1.20 m -> 0.024 m/px; target 80 px -> 1.92 m" or "f = 711 px; shelf edge \
300 px at 1.40 m -> 0.59 m".
Answer every question, in the order given, using its qid."""


def system_prompt(version: str = "v1") -> str:
    return {"v1": SYSTEM, "v2": SYSTEM_V2}[version]


def output_schema(version: str = "v1") -> dict:
    return {"v1": SCHEMA, "v2": SCHEMA_V2}[version]


# --------------------------------------------------------------------------- frames

_T_EQ = re.compile(r"\bt\s*=\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
_T_SEC = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s*(?:s|secs?|seconds?)\b", re.IGNORECASE)


def mentioned_times(texts: list[str]) -> list[float]:
    """Times in seconds named in question / prior / depth text ("t=1.5", "at 1.5s", "1.00s to 2.00s")."""
    found: set[float] = set()
    for text in texts:
        if not isinstance(text, str):
            continue
        for rx in (_T_EQ, _T_SEC):
            found.update(round(float(m.group(1)), 3) for m in rx.finditer(text))
    return sorted(found)


def _spread(items: list[int], k: int) -> list[int]:
    """k items evenly spread over `items` (all of them if k >= len)."""
    if k >= len(items):
        return list(items)
    if k <= 0:
        return []
    return [items[i] for i in sorted(set(np.linspace(0, len(items) - 1, k).round().astype(int)))]


def select_frames(n_total: int, fps: float, times: list[float], n_uniform: int = 16,
                  max_frames: int = 32, delta: float = 0.1) -> list[int]:
    """Uniform frames + frames nearest each mentioned time (t, t - delta, t + delta), deduplicated
    and capped at `max_frames`. Priority when over the cap: exact times, then +/- delta, then
    uniform (kept evenly spread)."""
    last = max(n_total - 1, 0)
    clip = lambda i: int(min(max(i, 0), last))  # noqa: E731
    exact = [clip(round(t * fps)) for t in times]
    near = [clip(round((t + s * delta) * fps)) for t in times for s in (-1, 1)]
    uniform = sorted(set(np.linspace(0, last, max(1, min(n_uniform, n_total))).round().astype(int).tolist()))
    chosen: list[int] = []
    for group in (list(dict.fromkeys(exact)), list(dict.fromkeys(near))):
        fresh = [i for i in group if i not in chosen]
        chosen += _spread(fresh, max_frames - len(chosen))
    rest = [i for i in uniform if i not in chosen]
    chosen += _spread(rest, max_frames - len(chosen))
    return sorted(chosen)


_T_WORD = re.compile(r"\btime\s*=?\s*(\d+(?:\.\d+)?)", re.IGNORECASE)              # "at time1.75 s"
_T_RANGE = re.compile(r"\b(?:from|between)\s+(\d+(?:\.\d+)?)\s*(?:s|secs?|seconds?)?\s*(?:to|and|-|until)\s*"
                      r"(\d+(?:\.\d+)?)\b", re.IGNORECASE)                       # "from 0.5 to 5.53"


def mentioned_times_v2(texts: list[str]) -> list[float]:
    """mentioned_times plus "time1.75" and both ends of "from A to B" when A or B has no unit."""
    found = set(mentioned_times(texts))
    for text in texts:
        if not isinstance(text, str):
            continue
        found.update(round(float(m.group(1)), 3) for m in _T_WORD.finditer(text))
        for m in _T_RANGE.finditer(text):
            found.update(round(float(g), 3) for g in m.groups())
    return sorted(found)


def select_frames_v2(n_total: int, fps: float, times: list[float], n_uniform: int = 16,
                     max_frames: int = 44, burst: int = 3, skip_first: bool = False) -> list[int]:
    """Prompt v2 frames: every frame of a clip that fits in `max_frames`; otherwise, by priority,
    the frame nearest each mentioned time, its immediate neighbours, uniform frames (at least one
    per 0.5 s: n_uniform raised to ceil(duration / 0.5), at most 32), the rest of a burst of
    +-`burst` consecutive frames around each time (step round(fps / 30) at high frame rates), then
    evenly spread frames up to the cap. skip_first drops frame 0 (when it repeats frame 1:
    frozen_first_frame), using frame 1."""
    first, last = (1 if skip_first and n_total > 1 else 0), max(n_total - 1, 0)
    if last - first + 1 <= max_frames:
        return list(range(first, last + 1))
    clip = lambda i: int(min(max(i, first), last))  # noqa: E731
    step = max(1, round(fps / 30))
    exact = [clip(round(t * fps)) for t in times]
    rings = [[clip(e + s * k * step) for e in exact for s in (-1, 1)] for k in range(1, burst + 1)]
    n_uni = int(np.clip(math.ceil(n_total / fps / 0.5), n_uniform, 32))
    uniform = sorted(set(np.linspace(first, last, max(1, min(n_uni, last - first + 1))).round().astype(int).tolist()))
    fill = sorted(set(np.linspace(first, last, max_frames).round().astype(int).tolist()))
    chosen: list[int] = []
    for group in (exact, rings[0] if rings else [], uniform, *rings[1:], fill):
        fresh = [i for i in dict.fromkeys(group) if i not in chosen]
        chosen += _spread(fresh, max_frames - len(chosen))
    return sorted(chosen)


def video_info(path: str) -> tuple[int, int, int]:
    """(frame_count, width, height) from the container header; frames are counted by decoding
    when the header has no count (<= 0)."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise FileNotFoundError(path)
    n, w, h = (int(cap.get(p)) for p in (cv2.CAP_PROP_FRAME_COUNT, cv2.CAP_PROP_FRAME_WIDTH,
                                         cv2.CAP_PROP_FRAME_HEIGHT))
    if n <= 0:
        n = 0
        while cap.grab():
            n += 1
    cap.release()
    return n, w, h


def video_fps(dataset_fps, path: str) -> tuple[float, bool]:
    """(fps, from_container): the dataset fps, or the container's when the dataset value is
    missing / NaN / <= 0. Raises ValueError when neither is usable."""
    fps = _num(dataset_fps)
    if fps is not None and fps > 0:
        return fps, False
    cap = cv2.VideoCapture(path)
    fps = _num(cap.get(cv2.CAP_PROP_FPS)) if cap.isOpened() else None
    cap.release()
    if fps is None or fps <= 0:
        raise ValueError(f"no usable fps for {path} (dataset {dataset_fps!r}, container {fps!r})")
    return fps, True


def frozen_first_frame(path: str, still: float = 0.1, moving: float = 0.5) -> bool:
    """True when frame 0 repeats frame 1 (mean absolute grey difference < `still`) while the video
    moves right after it (frame 1 -> 2 > `moving`): a renderer artifact in some simulations, where
    frame 0 is not a sample at t=0 (an object would stand still for one frame, then jump). False when
    the video cannot be read."""
    cap = cv2.VideoCapture(path)
    grey = []
    while len(grey) < 3 and cap.isOpened() and cap.grab():
        ok, img = cap.retrieve()
        if not ok:
            break
        grey.append(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32))
    cap.release()
    if len(grey) < 3:
        return False
    return float(np.abs(grey[0] - grey[1]).mean()) < still and float(np.abs(grey[1] - grey[2]).mean()) > moving


def read_frames(path: str, indices: list[int], fps: float, quality: int = 90,
                max_side: int = MAX_SIDE) -> tuple[list[Frame], float]:
    """Decode the given frame indices (sequential read: exact for any codec) as JPEG.
    Returns (frames, scale); scale < 1 only when the video exceeds `max_side`."""
    want, frames, scale = set(indices), [], 1.0
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise FileNotFoundError(path)
    i = 0
    while want and cap.grab():
        if i in want:
            ok, img = cap.retrieve()
            if ok:
                h, w = img.shape[:2]
                scale = min(1.0, max_side / max(h, w))
                if scale < 1.0:
                    img = cv2.resize(img, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_AREA)
                ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
                frames.append(Frame(i, i / fps, base64.b64encode(buf).decode(), img.shape[1], img.shape[0]))
            want.discard(i)
        i += 1
    cap.release()
    if not frames:
        raise RuntimeError(f"no frames decoded from {path}")
    return frames, scale


# --------------------------------------------------------------------------- request

def frame_label(f: Frame) -> str:
    return f"Frame {f.index} (t={f.time_s:.3f}s)"


def _question_block(row) -> str:
    depth = row.depth_info.strip() if isinstance(row.depth_info, str) and row.depth_info.strip() else ""
    return (f"Question qid={int(row.qid)}\n"
            f"Prior: {str(row.prior).strip()}\n"
            f"Depth info: {depth if depth else 'none (2D video)'}\n"
            f"Question: {row.question.strip()}\n"
            f"Asked unit: {row.target_unit or 'as stated in the question (SI: m, m/s or m/s^2 if none)'}")


def default_max_tokens(n_questions: int, prompt_version: str = "v1") -> int:
    """Room for adaptive thinking plus ~3-4k JSON tokens per question (v2, with a box on every
    frame of a moving 3D object and the range / derivation fields: ~5k)."""
    per_q = 5000 if prompt_version == "v2" else 4000
    return int(min(64000, 12000 + per_q * n_questions))


def default_max_side(prompt_version: str = "v1") -> int:
    """Long-edge cap of the frames sent: native up to MAX_SIDE (v1); 1280 px in v2, which pays for
    its denser frames on the 1080p-4K test videos (1280 px still exceeds every val video's 854)."""
    return MAX_SIDE if prompt_version == "v1" else 1280


def default_max_frames(prompt_version: str = "v1") -> int:
    return 32 if prompt_version == "v1" else 44


def frame_plan(rows: pd.DataFrame, n_total: int, fps: float, n_uniform: int, max_frames: int,
               prompt_version: str = "v1") -> tuple[list[int], bool]:
    """(frame indices to send, frame 0 skipped as a repeat of frame 1) for one video's questions."""
    texts = [t for r in rows.itertuples() for t in (r.question, r.prior, r.depth_info)]
    if prompt_version == "v1":
        return select_frames(n_total, fps, mentioned_times(texts), n_uniform, max_frames), False
    frozen = frozen_first_frame(str(rows.iloc[0].video_path))
    return select_frames_v2(n_total, fps, mentioned_times_v2(texts), n_uniform, max_frames,
                            skip_first=frozen), frozen


def _camera_note(row, width: int) -> str:
    """v2: the lab camera's focal length at the sent image width (3D lab videos only)."""
    if str(getattr(row, "video_source", "") or "") != "lab" or str(row.video_type)[1:2] != "3":
        return ""
    f = width / 2 / math.tan(math.radians(LAB_FOV_DEG) / 2)
    return (f" Camera: horizontal field of view about {LAB_FOV_DEG:g} deg, i.e. focal length about "
            f"{f:.0f} px at this image width (principal point at the image centre).")


def build_request(rows: pd.DataFrame, n_uniform: int = 16, max_frames: int = 0, effort: str = "medium",
                  max_tokens: int = 0, model: str = MODEL, quality: int = 90, prompt_version: str = "v1",
                  max_side: int = 0) -> tuple[dict, dict]:
    """Messages API params (also usable as a batch request's params) and the metadata needed to
    convert the answer back. `rows` are all questions of one video (qp.data columns).
    prompt_version "v1" is the original request (byte-identical, so cached v1 runs replay and
    recovered batches rebuild their metadata); "v2" = SYSTEM_V2 / SCHEMA_V2, select_frames_v2
    (bursts at asked times, all frames of short clips, frame 0 dropped when it repeats frame 1),
    frames capped at 1280 px and, for lab 3D videos, the camera's focal length in the text.
    max_frames / max_side 0 = the version's default."""
    if prompt_version not in PROMPT_VERSIONS:
        raise ValueError(f"unknown prompt_version {prompt_version!r}")
    max_frames = max_frames or default_max_frames(prompt_version)
    max_side = max_side or default_max_side(prompt_version)
    first = rows.iloc[0]
    path = str(first.video_path)
    fps, fps_from_container = video_fps(first.fps, path)
    n_total = video_info(path)[0]
    idxs, frozen = frame_plan(rows, n_total, fps, n_uniform, max_frames, prompt_version)
    frames, scale = read_frames(path, idxs, fps, quality, max_side)
    is_3d = str(first.video_type)[1:2] == "3"

    content: list[dict] = [{"type": "text", "text": (
        f"Video {first.video_id}: {'3D video with camera distances' if is_3d else '2D video'}; "
        f"{frames[0].width}x{frames[0].height} px; {fps:g} fps; {n_total} frames "
        f"(~{n_total / fps:.2f} s). {len(frames)} frames follow."
        + (_camera_note(first, frames[0].width) if prompt_version == "v2" else ""))}]
    for f in frames:
        content.append({"type": "text", "text": frame_label(f)})
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                                    "data": f.jpeg_b64}})
    blocks = "\n\n".join(_question_block(r) for r in rows.itertuples())
    content.append({"type": "text", "text": (
        f"{len(rows)} question(s) about this video (fps {fps:g}, image size "
        f"{frames[0].width}x{frames[0].height} px):\n\n{blocks}")})

    params = {
        "model": model,
        "max_tokens": max_tokens or default_max_tokens(len(rows), prompt_version),
        "system": [{"type": "text", "text": system_prompt(prompt_version), "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": content}],
        "output_config": {"effort": effort, "format": {"type": "json_schema",
                                                       "schema": output_schema(prompt_version)}},
    }
    meta = {
        "video_id": str(first.video_id), "fps": fps, "fps_from_container": fps_from_container,
        "video_type": str(first.video_type), "n_frames_total": n_total, "scale": scale,
        "image_size": [round(frames[0].width / scale), round(frames[0].height / scale)],  # (w, h) original
        "frames": [f.index for f in frames],
        "questions": [{"qid": int(r.qid), "target_unit": r.target_unit, "prior": str(r.prior),
                       "depth_info": str(r.depth_info or "")} for r in rows.itertuples()],
        "prompt_version": prompt_version,
    }
    if frozen:
        meta["frozen_first_frame"] = True
    return params, meta


def estimate_input_tokens(params: dict) -> int:
    """Offline estimate (no API call): images ~ w*h/750 tokens, text ~ 3.5 chars/token, plus
    ~3000 tokens for the output schema and formatting (calibrated on one live request: 9.7k
    actual vs 10.4k estimated). Prefer client.messages.count_tokens."""
    n, chars = 3000, sum(len(b["text"]) for b in params["system"])
    for block in params["messages"][0]["content"]:
        if block["type"] == "text":
            chars += len(block["text"])
        else:
            img = cv2.imdecode(np.frombuffer(base64.b64decode(block["source"]["data"]), np.uint8),
                               cv2.IMREAD_UNCHANGED)
            n += math.ceil(img.shape[0] * img.shape[1] / 750)
    return n + math.ceil(chars / 3.5)


# --------------------------------------------------------------------------- response

@dataclass
class Annotation:
    spec: QuestionSpec
    tracks: list[RoleTrack]
    direct_answer: float | None
    confidence: float | None
    flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def response_text(message) -> str:
    """Concatenated text blocks of a Message (thinking blocks skipped)."""
    return "".join(b.text for b in message.content if getattr(b, "type", "") == "text")


def _num(x) -> float | None:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def _xy(p) -> list[float] | None:
    if isinstance(p, (list, tuple)) and len(p) == 2 and all(_num(v) is not None for v in p):
        return [float(p[0]), float(p[1])]
    return None


def _quantity(d: dict, flags: list[str], who: str) -> Quantity:
    kind = d.get("kind", "other")
    if kind not in KINDS:
        flags.append(f"{who}_kind_{kind}")
        kind = "other"
    window = d.get("window")
    window = [float(window[0]), float(window[1])] if _xy(window) else None
    axis = d.get("axis", "any")
    return Quantity(kind=kind, objects=[str(o) for o in d.get("objects") or []],
                    dimension=str(d.get("dimension") or ""), time=_num(d.get("time")), window=window,
                    axis=axis if axis in AXES else "any", value_si=_num(d.get("value_si")),
                    unit=str(d.get("unit") or ""))


def _obs(o: dict, fps: float, inv: float, sent: set[int], flags: list[str]) -> Obs | None:
    frame = o.get("frame")
    if not isinstance(frame, int) or frame not in sent:
        flags.append("unknown_frame")
        return None
    point = _xy(o.get("point"))
    ext = o.get("extent")
    extent = [_xy(ext[0]), _xy(ext[1])] if isinstance(ext, list) and len(ext) == 2 else None
    extent = extent if extent and all(extent) else None
    box = o.get("box")
    box = [float(v) for v in box] if isinstance(box, list) and len(box) == 4 and all(
        _num(v) is not None for v in box) else None
    if box:
        box = [min(box[0], box[2]), min(box[1], box[3]), max(box[0], box[2]), max(box[1], box[3])]
    if point is None and extent is None and box is None:
        return None
    s = lambda v: [x * inv for x in v]  # noqa: E731 - back to original-frame pixels
    return Obs(t=frame / fps, point=s(point) if point else None,
               extent=[s(p) for p in extent] if extent else None, box=s(box) if box else None)


_PRIOR_NUM = re.compile(r"[=~≈]\s*[~≈]?\s*([-−]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)")
_PRIOR_UNIT = re.compile(r"\s*(" + _UNIT + r")(?![A-Za-z])", re.IGNORECASE)
_SECONDS = re.compile(r"\s*s(?:ec(?:ond)?s?)?\b", re.IGNORECASE)
_GRAVITY = re.compile(r"gravit|free.?fall", re.IGNORECASE)
_ACCEL_WORD = re.compile(r"acceler|gravit|\bacc\b|free.?fall", re.IGNORECASE)
_TNUM = r"(\d+(?:\.\d+)?)"
_PRIOR_BEFORE = re.compile(rf"\bbefore\s+(?:t\s*=\s*)?{_TNUM}\s*s(?:ec(?:ond)?s?)?\b", re.IGNORECASE)
_PRIOR_AFTER = re.compile(rf"\bafter\s+(?:t\s*=\s*)?{_TNUM}\s*s(?:ec(?:ond)?s?)?\b", re.IGNORECASE)
_PRIOR_FROM_TO = re.compile(rf"\bfrom\s+(?:t\s*=\s*)?{_TNUM}\s*s?\s*(?:to|until|-)\s*(?:t\s*=\s*)?{_TNUM}\s*s\b",
                            re.IGNORECASE)


def prior_si(prior_text: str) -> tuple[float, str] | None:
    """(value in SI, dimension "L"/"V"/"A", or "" when no unit is given) of the known quantity in
    a prior text: the last number after "=" / "~" that is not a time ("t=1.5", "at 1.5s = ..."),
    with the unit right after it ("57.2mm" -> 0.0572, "~1.1 m/s" -> 1.1). A sign is dropped
    ("acceleration = -2.86m/s^2" -> 2.86: every quantity is a magnitude). None when there is no
    such number or its unit is not recognised."""
    text = prior_text if isinstance(prior_text, str) else ""
    for m in reversed(list(_PRIOR_NUM.finditer(text))):
        rest = text[m.end():]
        if re.search(r"\bt\s*$", text[:m.start()], re.IGNORECASE) or _SECONDS.match(rest):
            continue  # a time, not the value
        value, u = abs(float(m.group(1).replace("−", "-"))), _PRIOR_UNIT.match(rest)
        if u:
            cu = canonical_unit(u.group(1))
            return (value * _UNITS[cu][0], _UNITS[cu][1]) if cu in _UNITS else None
        return None if re.match(r"\s*[A-Za-z]", rest) else (value, "")
    return None


def prior_dimension(prior_text: str, unit_dim: str) -> str:
    """Dimension of the prior: the unit's ("L"/"V"/"A"), except that a velocity unit on a quantity
    the text names an acceleration ("acceleration of the box = 9.8m/s", "gravity acc = 9.8m/s") is a
    unit typo, not a speed: "A" (m/s and m/s^2 share the scale, so the value stays)."""
    if unit_dim == "V" and _ACCEL_WORD.search(prior_text or "") and not re.search(
            r"\b(?:speed|velocity)\b", prior_text or "", re.IGNORECASE):
        return "A"
    return unit_dim


def prior_time_span(prior_text: str, t_end: float | None = None) -> tuple[float | None, list[float] | None] | None:
    """(time, window) a prior text states with "before T" ([0, T]), "after T" ([T, t_end]) or
    "from A to B" ([A, B]); None when it states none of these (an "at T" prior keeps the model's
    time). "after T" needs t_end (the clip's last frame time)."""
    text = prior_text if isinstance(prior_text, str) else ""
    if m := _PRIOR_FROM_TO.search(text):
        a, b = float(m.group(1)), float(m.group(2))
        return (None, [min(a, b), max(a, b)]) if b != a else None
    if m := _PRIOR_BEFORE.search(text):
        return (None, [0.0, float(m.group(1))]) if float(m.group(1)) > 0 else None
    if (m := _PRIOR_AFTER.search(text)) and t_end is not None and t_end > float(m.group(1)):
        return None, [float(m.group(1)), float(t_end)]
    return None


# --------------------------------------------------------------------------- depth info text

_DEPTH_ENTRY = re.compile(
    r"(?:\bt\s*=\s*(?P<t>\d+(?:\.\d+)?)\s*(?:s(?:ec(?:ond)?s?)?)?(?![A-Za-z])(?:\s*\([^)]*\))?\s*[,;:]?\s*)?"
    r"(?:the\s+)?distance[_\s]*(?:between[_\s]+|of[_\s]+|from[_\s]+)?(?P<obj>[^=:\n]+?)\s*[=:]\s*[~≈]?\s*"
    r"(?P<d>\d+(?:\.\d+)?)\s*(?P<u>mm|cm|km|m|met(?:er|re)s?|s)?(?![A-Za-z])",
    re.IGNORECASE)
_DEPTH_UNIT = {"mm": 1e-3, "cm": 1e-2, "km": 1e3, "s": 1.0}  # "...=0.8715s": a typo for m


def _depth_name(raw: str) -> str:
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", raw)              # yellowCarLeftFrontTire
    s = re.sub(r"[_\s]+", " ", s).strip().lower()
    s = re.sub(r"^camera\s+(?:and\s+|to\s+)?", "", s)          # distance_camera_B1sign
    s = re.sub(r"\s*\b(?:and|to|from)?\s*(?:the\s+)?camera$", "", s)  # ..._and_camera / ..._camera
    s = re.sub(r"^(?:the|a|an)\s+", "", s)
    return s.strip() or raw.strip()


def parse_depth_info(text: str) -> list[DepthEntry]:
    """Depth entries of a depth_info text, deterministically: one per "[t=<s>s[ (remark)],]
    distance_<object>[_and]_camera = <d> m" (units mm/cm/km/m; a trailing "s" is read as m);
    object names cleaned of underscores, camelCase, "camera" and a leading "the". [] if none."""
    out: list[DepthEntry] = []
    for m in _DEPTH_ENTRY.finditer(text if isinstance(text, str) else ""):
        u = (m.group("u") or "m").lower()
        d = float(m.group("d")) * _DEPTH_UNIT.get(u, 1.0)
        if d > 0:
            out.append(DepthEntry(object=_depth_name(m.group("obj")), distance_m=d,
                                  time=float(m.group("t")) if m.group("t") else None))
    return out


def prior_value_consistent(prior_text: str, value_si: float | None) -> bool:
    """True if value_si matches the prior text's value in SI (within 1%). When the text does not
    parse (prior_si is None), any number in it times a unit scale (mm, cm, km/h ...) is accepted."""
    if value_si is None or value_si <= 0:
        return False
    parsed = prior_si(prior_text)
    if parsed is not None:
        return abs(value_si - parsed[0]) <= 1e-2 * parsed[0]
    scales = {s for s, _ in _UNITS.values()} | {1.0}
    for m in re.finditer(r"\d+(?:\.\d+)?", prior_text or ""):
        if any(abs(float(m.group()) * s - value_si) <= 1e-3 * value_si for s in scales):
            return True
    return False


def _dim(text: str) -> str:
    return re.sub(r"[^a-z]", "", str(text or "").casefold())


def _reusable(earlier: list[tuple[Quantity, list[Obs]]], q: Quantity, fps: float | None = None) -> list[Obs] | None:
    """Obs of the earlier same-name track that carries what quantity `q` needs: for motion and
    distances the one with the most points (then boxes); for a size the one with the most extents
    among tracks measuring the same dimension. A distance at a time needs a located (point or box)
    obs within max(0.5 s, 2 frames) of it: a track from another moment cannot stand in. None if no
    earlier track fits (camera_distance needs no observations)."""
    if q.kind == "camera_distance":
        return None
    if q.kind in ("size", "other"):
        want = _dim(q.dimension)
        cands = [obs for eq, obs in earlier if eq.kind in ("size", "other")
                 and (not want or not _dim(eq.dimension) or _dim(eq.dimension) == want)]
        key = lambda obs: (sum(o.extent is not None for o in obs), 0)  # noqa: E731
    else:
        cands = [obs for _, obs in earlier]
        t = q.time if q.kind == "distance" else None
        if t is not None and math.isfinite(t):
            tol = max(0.5, 2.0 / fps) if fps else 0.5
            cands = [obs for obs in cands
                     if any((o.point is not None or o.box is not None) and abs(o.t - t) <= tol for o in obs)]
        key = lambda obs: (sum(o.point is not None for o in obs), sum(o.box is not None for o in obs))  # noqa: E731
    best = max(cands, key=key, default=None)
    return best if best is not None and any(key(best)) else None


MOTION_KINDS = ("speed", "acceleration", "displacement", "path_length")


def to_annotations(parsed: dict, meta: dict, source: str = "claude") -> dict[int, Annotation]:
    """Model JSON -> {qid: Annotation}. Pixel coords mapped back to original frames; Obs.t is
    frame_idx / dataset fps; is_3d from video_type[1]; the target unit comes from the question
    text (qp.data.target_unit) when available, else from the model; prior.value_si comes from the
    prior text (prior_si) when it parses, else from the model, and the text's unit fixes the prior
    kind's dimension (a velocity unit on an acceleration is a typo: prior_dimension); a motion
    prior stated "before T" / "after T" / "from A to B" gets that window (prior_time_span); a
    gravity prior gets axis "vertical" (what qp.geometry keys gravity on). The depth list is parsed
    from the question's depth_info text (meta["questions"][i]["depth_info"]) when it has entries,
    else taken from the model. An empty track reuses an earlier track of the same object that
    carries what its quantity needs (_reusable)."""
    fps, inv = float(meta["fps"]), 1.0 / float(meta.get("scale", 1.0) or 1.0)
    sent, is_3d = set(meta["frames"]), str(meta["video_type"])[1:2] == "3"
    n_total = _num(meta.get("n_frames_total"))
    t_end = (n_total - 1) / fps if n_total and n_total > 1 else None
    rows = {q["qid"]: q for q in meta["questions"]}
    seen: dict[str, list[tuple[Quantity, list[Obs]]]] = {}  # object name -> earlier (quantity, obs)
    out: dict[int, Annotation] = {}
    for q in parsed.get("questions", []):
        try:
            qid = int(q["qid"])
        except (KeyError, TypeError, ValueError):
            continue
        if qid not in rows or qid in out:
            continue
        flags: list[str] = []
        s = q.get("spec") or {}
        target = _quantity(s.get("target") or {}, flags, "target")
        prior = _quantity(s.get("prior") or {}, flags, "prior")
        unit = rows[qid]["target_unit"] or canonical_unit(target.unit) or target.unit
        target.unit, target.value_si, prior.unit = unit, None, ""
        prior_text = rows[qid]["prior"]
        parsed_prior = prior_si(prior_text)
        if parsed_prior is None:  # keep the model's value (a magnitude)
            flags.append("prior_value_unverified")
            prior.value_si = abs(prior.value_si) if prior.value_si is not None else None
        else:  # the text is authoritative: catches mm/cm/m slips and times taken as the value
            value, dim = parsed_prior
            if prior.value_si is None or abs(abs(prior.value_si) - value) > 1e-2 * value:
                flags.append("prior_value_model_mismatch")
            if dim and (fixed := prior_dimension(prior_text, dim)) != dim:
                flags.append("prior_unit_typo")
                dim = fixed
            if dim and dim != KIND_DIM.get(prior.kind):  # the unit decides the dimension (as qwen_vl)
                flags.append("prior_kind_unit_mismatch")
                prior.kind = {"V": "speed", "A": "acceleration"}.get(dim, "size")
            prior.value_si = value
        span = prior_time_span(prior_text, t_end) if prior.kind in MOTION_KINDS else None
        if span is not None:
            if (prior.time, prior.window) != span:
                flags.append("prior_window_from_text")
            prior.time, prior.window = span
        if prior.kind == "acceleration" and prior.axis != "vertical" and _GRAVITY.search(prior_text):
            flags.append("prior_axis_gravity")  # qp.geometry treats a vertical acceleration prior as gravity
            prior.axis = "vertical"
        if meta.get("fps_from_container"):
            flags.append("fps_from_container")
        depth = []
        for e in s.get("depth") or []:
            dist = _num(e.get("distance_m"))
            if dist is not None and dist > 0:
                depth.append(DepthEntry(object=str(e.get("object", "")), distance_m=dist, time=_num(e.get("time"))))
        text_depth = parse_depth_info(rows[qid].get("depth_info", ""))
        if text_depth:  # the fixed-format text is authoritative (the model sometimes omits the list)
            if not depth and meta.get("prompt_version", "v1") == "v1":  # v2 asks for an empty list
                flags.append("model_depth_empty")
            depth = text_depth
        if is_3d and not depth:
            flags.append("no_depth")
        spec = QuestionSpec(qid=qid, target=target, prior=prior, depth=depth, is_3d=is_3d,
                            notes=str(s.get("notes") or ""))
        tracks = []
        for tr in q.get("tracks") or []:
            role, name = tr.get("role"), str(tr.get("object", ""))
            if role not in ROLES:
                continue
            obs = [ob for o in tr.get("obs") or [] if (ob := _obs(o, fps, inv, sent, flags))]
            key, quantity = name.strip().casefold(), prior if role.startswith("prior") else target
            if not obs and seen.get(key) and quantity.kind != "camera_distance":
                reuse = _reusable(seen[key], quantity, fps)
                obs = [Obs(**asdict(o)) for o in reuse or []]
                flags.append("reused_track" if reuse else "reuse_unavailable")
            elif obs:
                seen.setdefault(key, []).append((quantity, obs))
            rng = _num(tr.get("range_m"))
            tracks.append(RoleTrack(role=role, object=name, obs=sorted(obs, key=lambda o: o.t), source=source,
                                    depth_name=str(tr.get("depth_name") or "").strip(),
                                    range_m=rng if rng is not None and rng > 0 else None))
        direct = _num(q.get("direct_answer"))
        out[qid] = Annotation(spec=spec, tracks=tracks,
                              direct_answer=direct if direct is not None and direct > 0 else None,
                              confidence=_num(q.get("confidence")), flags=sorted(set(flags)))
    return out


def with_depth_info(record: dict, depth_texts: dict[int, str]) -> dict:
    """A copy of a run_claude record whose meta questions carry their depth_info text (taken from
    `depth_texts`, {qid: text}, where the record lacks it): records made before the text was stored
    in meta would otherwise keep the model's depth list. The record on disk is untouched."""
    meta = record.get("meta")
    if not isinstance(meta, dict) or not meta.get("questions"):
        return record
    qs = [{**q, "depth_info": q.get("depth_info", depth_texts.get(int(q["qid"]), "") or "")}
          for q in meta["questions"]]
    return {**record, "meta": {**meta, "questions": qs}}


def load_annotations(records: dict[str, dict]) -> dict[int, Annotation]:
    """{qid: Annotation} from run_claude records ({video_id: record}) with status "ok" or
    "partial" (some qids missing from the response), plus the complete questions of a response cut
    off at max_tokens (salvage_questions of its raw text)."""
    out: dict[int, Annotation] = {}
    for rec in records.values():
        if rec.get("status") in ("ok", "partial") and rec.get("parsed"):
            out.update(to_annotations(rec["parsed"], rec["meta"]))
        elif rec.get("status") == "max_tokens" and rec.get("meta") and (got := salvage_questions(rec.get("raw_text"))):
            out.update(to_annotations(got, rec["meta"]))
    return out


def salvage_questions(text) -> dict | None:
    """{"questions": [...]} with the complete question objects of a JSON response cut off mid-way
    (stop reason max_tokens): '{"questions":[{...},{...},{"qid":12,"spec":{...' -> the first two.
    Structured outputs emit the questions in order, so every object before the cut is whole. None
    when no complete question precedes the cut (or the text is not such a response)."""
    if not isinstance(text, str):
        return None
    m = re.match(r'\s*\{\s*"questions"\s*:\s*\[', text)
    if not m:
        return None
    dec, pos, got = json.JSONDecoder(), m.end(), []
    while True:
        while pos < len(text) and text[pos] in " \t\r\n,":
            pos += 1
        try:
            obj, pos = dec.raw_decode(text, pos)
        except ValueError:
            break
        if isinstance(obj, dict) and "qid" in obj:
            got.append(obj)
    return {"questions": got} if got else None


def parse_json(text: str) -> dict | None:
    try:
        data = json.loads(text)
    except (TypeError, ValueError):
        return None
    return data if isinstance(data, dict) else None
