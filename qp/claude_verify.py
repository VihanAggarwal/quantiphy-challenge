"""Verification pass: a second Claude request per video that checks and corrects the pixel
measurements behind each pass-1 answer (scripts/run_claude.py records).

Pass 1 (qp.claude_annotate) places extents / points / boxes on whole frames; at 5% tolerance a few
pixels decide the score. This pass shows Claude what pass 1 measured, drawn on the frames, with
zoomed crops around every endpoint so each one can be checked at pixel level, and asks it per track
to keep or replace the measurement (in ORIGINAL pixel coordinates) and per question to accept or
fix the spec. Our code applies the corrections and recomputes the geometry (qp.geometry.solve);
the model's own arithmetic is only used as a consistency check.

    ctxs = build_contexts(df, pass1_records)                 # {video_id: VideoContext}
    params, meta = build_request(ctxs[vid], effort="high")    # Messages API / batch params
    rows = recompute(meta, parsed_json)                       # one result row per question

Request versions (SYSTEMS): vf1 asks for coordinates only with action "replace"; vf2 (default) asks
for the model's own reading of every evidence frame of every track ("keep" or not), which the
`remeasure` rule and the delta_px diagnostic need. The one live test (vf1, internet_0005, effort
medium, $0.088) kept every track, but that was the right output: three answers were within 2% and
the fourth (qid 2167, +30%) has its extent within ~1 px of the light's ends (an object-choice or
ground-truth issue, not endpoint placement), so it says nothing about vf1's diligence, and vf2 /
effort high are untested. A smoke test that can tell them apart needs questions whose pass-1 error is a visible
endpoint misplacement.

Tracks. The tracks of a video's questions are deduplicated (same object, same observations ->
one track id "A", "B", ...), so a correction of a shared track (typically the prior) applies to
every question using it. What the geometry reads from a track decides its evidence ("use"):
  size      extent endpoints (else box sides): the median-length obs and one more frame
  motion    points over time: the obs at the window ends / around the asked time / first-middle-last
  distance  points at the asked time (both objects on the same frame)
Evidence images: one full frame per evidence frame index (downscaled to max_side, all marks of
that frame drawn: extents as segments with endpoint circles, boxes, a motion track's whole path
with timestamps, a distance as a dashed segment) and crops around each endpoint / point,
zoomed 2-4x, with tick labels in original-pixel units on the margins (MARGIN_L / MARGIN_T px of tick
band before the picture). Each image is preceded by a text line giving its frame, region (x0..x1,
y0..y1) and zoom (scale for full frames), so original x = x0 + (u - MARGIN_L) / zoom, y = y0 +
(v - MARGIN_T) / zoom for an image pixel (u, v); the prompt states this with the numbers.

Answer rule (RULES; DEFAULT_RULE = "verify"), per question, with pass1 = the pass-1 selection
(qp.combine.choose on the pass-1 geometry and direct answers, exactly as run_claude.build_results):
  verify          verdict accept_direct -> pass-1 direct answer. Else, if a correction touched the
                  question (one of its tracks replaced, or its spec fixed) and the recomputed
                  geometry is valid and within VERIFY_AGREE x of the verifier's final_answer
                  (the coordinates mean what the model meant): qp.combine.choose on the
                  recomputed geometry and the pass-1 direct answer (same routing as pass 1:
                  3D questions of unknown cameras still go to the direct answer). Otherwise pass1.
  remeasure       as verify, but tracks read only for sizes / distances always take the verifier's
                  own readings (vf2 asks for a reading of every evidence frame of every track,
                  "keep" or not); tracks with a motion use change only on "replace"
Corrections never shrink a size / distance track to the evidence frames: the readings are merged into
the pass-1 track (merge_readings: read frames take the readings, the other frames the same systematic
change: length ratio / shift), so readings equal to pass 1 leave every answer of every rule unchanged.
A motion track marked "replace" becomes exactly the readings, unless they all agree with pass 1 within
NOOP_PX (then the dense / flow-refined pass-1 track is kept).
  verify_vdirect  as verify, with the verifier's final_answer as the direct answer wherever
                  the verifier changed or rejected something (verdict != accept_geometry)
  verify_final    the verifier's final_answer (diagnostic: the model's own arithmetic)
  pass1           the pass-1 selection (no change; the baseline)
Every rule falls back to pass1 when its value is missing.
"""

from __future__ import annotations

import base64
import copy
import json
import math
from dataclasses import asdict, dataclass, field

import cv2
import numpy as np
import pandas as pd

from . import claude_annotate as ca
from . import combine
from .spec import KIND_DIM, KINDS, Answer, Obs, Quantity, QuestionSpec, RoleTrack

MODEL = ca.MODEL
VERIFY_VERSION = "vf2"           # default request version (SYSTEMS)
RULES = ("verify", "remeasure", "verify_vdirect", "verify_final", "pass1")
DEFAULT_RULE = "verify"
VERDICTS = ("accept_geometry", "corrected", "accept_direct")
ACTIONS = ("keep", "replace")
SPEC_FIELDS = ("kind", "objects", "dimension", "time", "window", "axis")
VERIFY_AGREE = 1.3        # recomputed geometry vs the verifier's final_answer: beyond this ratio the
                          # parsed coordinates are not what the model meant -> pass1. Below 1.5, the
                          # factor of coordinates read off a 1080p overview (1280/1920) as original;
                          # apply_track_fixes also checks the readings themselves (pixel_space_suspect)
GEO_MAX_SI = combine.GEO_MAX_SI
MOTION = ca.MOTION_KINDS
MAX_SIDE = 1280           # overview frames: long-edge cap (val 480p stays native)
MAX_OVERVIEWS = 16        # per request
MAX_CROPS = 48            # per request
SIZE_FRAMES = 2           # evidence frames per size track
MOTION_FRAMES = 4         # ... per motion / distance track
LIST_OBS = 12             # tracks with more obs list only their evidence frames' coordinates
CROP_OUT_PX = 360         # target side of a zoomed crop (sets the zoom, 2-4x)
JPEG_QUALITY = 92
MARGIN_L, MARGIN_T, MARGIN_R, MARGIN_B = 46, 24, 8, 8   # tick-label bands around every image

# BGR colours, with the names used in the text
PALETTE = [("cyan", (255, 255, 0)), ("magenta", (255, 0, 255)), ("yellow", (0, 255, 255)),
           ("orange", (0, 140, 255)), ("lime", (0, 255, 0)), ("red", (0, 0, 255)),
           ("blue", (255, 120, 0)), ("pink", (190, 120, 255)), ("white", (255, 255, 255)),
           ("teal", (160, 160, 0))]


def _tid(i: int) -> str:
    """Track ids A..Z, then A1..Z1, ..."""
    return chr(ord("A") + i % 26) + (str(i // 26) if i >= 26 else "")


def _r(x, nd: int = 1):
    return None if x is None else round(float(x), nd)


def _xy_txt(p) -> str:
    return f"({p[0]:.1f}, {p[1]:.1f})"


def valid(v) -> bool:
    return combine.valid(v)


# --------------------------------------------------------------------------- pass-1 context

@dataclass
class Track:
    tid: str
    object: str
    obs: list[Obs]
    depth_name: str = ""
    range_m: float | None = None
    source: str = ""
    refined: bool = False
    uses: list[dict] = field(default_factory=list)   # {"qid", "role", "use"}

    def to_dict(self) -> dict:
        return {"tid": self.tid, "object": self.object, "obs": [asdict(o) for o in self.obs],
                "depth_name": self.depth_name, "range_m": self.range_m, "source": self.source,
                "refined": self.refined, "uses": self.uses}

    @staticmethod
    def from_dict(d: dict) -> "Track":
        return Track(tid=d["tid"], object=d["object"], obs=[Obs(**o) for o in d["obs"]],
                     depth_name=d.get("depth_name", "") or "", range_m=d.get("range_m"),
                     source=d.get("source", ""), refined=bool(d.get("refined")), uses=list(d.get("uses") or []))


@dataclass
class QCtx:
    qid: int
    question: str
    prior_text: str
    depth_info: str
    category: str
    spec: QuestionSpec
    roles: list[list[str]]          # [[role, tid], ...] in the annotation's track order
    direct: float | None
    confidence: float | None
    ann_flags: list[str]
    dense_value: float | None = None


@dataclass
class VideoContext:
    video_id: str
    video_path: str
    fps: float
    image_size: tuple[int, int]     # original (W, H)
    n_frames: int
    video_type: str
    video_source: str
    tracks: dict[str, Track]
    questions: list[QCtx]

    @property
    def is_3d(self) -> bool:
        return str(self.video_type)[1:2] == "3"


def role_tracks(q: QCtx, tracks: dict[str, Track]) -> list[RoleTrack]:
    """The question's RoleTracks (as pass 1 gave them to the geometry) from the track table."""
    out = []
    for role, tid in q.roles:
        t = tracks[tid]
        out.append(RoleTrack(role=role, object=t.object, obs=[Obs(**asdict(o)) for o in t.obs], source=t.source,
                             depth_name=t.depth_name, range_m=t.range_m))
    return out


def solve_question(spec: QuestionSpec, tracks: list[RoleTrack], image_size, fps: float, video_source: str) -> Answer:
    """qp.geometry.solve with the same settings as scripts/run_claude.build_results (lab 3D videos:
    the known lab camera)."""
    from .geometry import solve
    fov = ca.LAB_FOV_DEG if str(video_source or "") in combine.CAMERA_SOURCES and spec.is_3d else None
    return solve(spec, tracks, tuple(image_size), float(fps), **({"camera_fov_deg": fov} if fov else {}))


def select(geo: Answer | None, direct: float | None, ann_flags: list[str], spec: QuestionSpec,
           video_source: str, rule: str = combine.DEFAULT_RULE) -> tuple[float, str, list[str]]:
    """(value, how, flags) exactly as scripts/run_claude.build_results selects between the geometry
    answer and a direct answer."""
    flags = list(ann_flags)
    gv = method = None
    if geo is not None:
        gv, method = geo.value, geo.method
        flags += [f"geo:{f}" for f in geo.flags]
        gsi = geo.debug.get("value_si")
        if valid(gv) and valid(gsi) and gsi > GEO_MAX_SI.get(KIND_DIM.get(spec.target.kind, "L"), math.inf):
            flags.append("geo_rejected_implausible")
    value, how, added = combine.choose(gv, direct if valid(direct) else None, flags, spec.is_3d, video_source,
                                       method or "", rule)
    return value, how, sorted(set(flags + added))


def _use(q: Quantity, role: str, has_partner: bool) -> str:
    kind = q.kind if q.kind in KINDS else "other"
    if kind == "camera_distance":
        return "none"
    if kind in ("size", "other"):
        return "size"
    if kind == "distance":   # a lone first object of a distance is its extent (qp.geometry: distance_from_extent)
        return "distance" if has_partner or role.endswith("2") else "size"
    return "motion"


def _signature(t: RoleTrack) -> str:
    obs = [(round(o.t, 4), o.point, o.extent, o.box) for o in t.obs]
    return json.dumps([str(t.object).strip().casefold(), t.depth_name or "", t.range_m, obs], default=float)


def load_dense(path: str) -> tuple[dict[int, list[RoleTrack]], dict[int, float]]:
    """--dense input: a .csv (columns id and parsed_value or geo_value: a dense-tracking run's answers,
    shown to the verifier as another candidate) or a .json file / directory of .json files mapping
    qid -> list of RoleTrack dicts (or {"tracks": [...]}) that replace pass 1's tracks of the same role."""
    from pathlib import Path
    p = Path(path)
    tracks: dict[int, list[RoleTrack]] = {}
    values: dict[int, float] = {}
    if p.suffix.lower() == ".csv":
        d = pd.read_csv(p)
        col = next((c for c in ("parsed_value", "geo_value", "value") if c in d.columns), None)
        if col is None or "id" not in d.columns:
            raise ValueError(f"{path}: need columns id and parsed_value / geo_value")
        values = {int(i): float(v) for i, v in zip(d["id"], d[col]) if valid(v)}
        return tracks, values
    files = sorted(p.glob("*.json")) if p.is_dir() else [p]
    for f in files:
        data = json.loads(f.read_text())
        for k, v in data.items():
            trs = v.get("tracks", []) if isinstance(v, dict) else v
            tracks[int(k)] = [RoleTrack.from_dict(t) for t in trs]
    return tracks, values


def build_contexts(df: pd.DataFrame, records: dict[str, dict], refine_priors: bool = True,
                   dense: tuple[dict, dict] | None = None, log: list | None = None) -> dict[str, VideoContext]:
    """{video_id: VideoContext} from pass-1 run_claude records ({video_id: record}) and the split's
    questions table: the annotations (ok / partial records), motion-prior tracks refined by optical flow
    as in build_results (refine_priors), optional dense tracks / values (load_dense), deduplicated tracks."""
    from . import refine
    texts = {int(q): str(t or "") for q, t in zip(df["qid"], df["depth_info"])}
    recs = {v: ca.with_depth_info(r, texts) for v, r in records.items() if v in set(df.video_id)}
    anns = ca.load_annotations(recs)
    if refine_priors:
        rows = [r for r in df.itertuples() if getattr(r, "video_path", "") and int(r.qid) in anns
                and (recs.get(r.video_id) or {}).get("meta")]
        try:
            refine.refine_annotations(
                anns, {int(r.qid): str(r.video_path) for r in rows},
                {int(r.qid): (float(recs[r.video_id]["meta"]["fps"]), tuple(recs[r.video_id]["meta"]["image_size"]))
                 for r in rows}, log=log)
        except Exception as e:  # noqa: BLE001 - refinement is optional
            print(f"prior refinement skipped: {type(e).__name__}: {e}")
    dense_tracks, dense_values = dense or ({}, {})
    out: dict[str, VideoContext] = {}
    for vid, g in df.groupby("video_id", sort=False):
        rec = recs.get(vid)
        if not rec or not rec.get("meta"):
            continue
        meta = rec["meta"]
        sigs: dict[str, str] = {}
        tracks: dict[str, Track] = {}
        qs: list[QCtx] = []
        for r in g.itertuples():
            a = anns.get(int(r.qid))
            if a is None:
                continue
            trs = list(a.tracks)
            flags = list(a.flags)
            if int(r.qid) in dense_tracks:
                new = dense_tracks[int(r.qid)]
                roles_new = {t.role for t in new}
                trs = [t for t in trs if t.role not in roles_new] + new
                flags.append("dense_tracks")
            roles = []
            for t in trs:
                sig = _signature(t)
                if sig not in sigs:
                    tid = _tid(len(tracks))
                    sigs[sig] = tid
                    tracks[tid] = Track(tid=tid, object=str(t.object), obs=[Obs(**asdict(o)) for o in t.obs],
                                        depth_name=t.depth_name or "", range_m=t.range_m, source=t.source,
                                        refined="prior_track_refined" in a.flags and t.role.startswith("prior")
                                        and a.spec.prior.kind in MOTION)
                tid = sigs[sig]
                roles.append([t.role, tid])
                has_partner = any(x.role == (t.role + "2" if not t.role.endswith("2") else t.role[:-1]) and x.obs
                                  for x in trs)
                q = a.spec.prior if t.role.startswith("prior") else a.spec.target
                use = {"qid": int(r.qid), "role": t.role, "use": _use(q, t.role, has_partner)}
                if use not in tracks[tid].uses:
                    tracks[tid].uses.append(use)
            qs.append(QCtx(qid=int(r.qid), question=str(r.question), prior_text=str(r.prior),
                           depth_info=str(r.depth_info or ""), category=str(getattr(r, "category", "")),
                           spec=a.spec, roles=roles, direct=a.direct_answer, confidence=a.confidence,
                           ann_flags=sorted(set(flags)), dense_value=dense_values.get(int(r.qid))))
        if not qs:
            continue
        first = g.iloc[0]
        out[vid] = VideoContext(video_id=str(vid), video_path=str(first.video_path), fps=float(meta["fps"]),
                                image_size=tuple(int(x) for x in meta["image_size"]),
                                n_frames=int(meta.get("n_frames_total") or 0), video_type=str(first.video_type),
                                video_source=str(getattr(first, "video_source", "") or ""), tracks=tracks, questions=qs)
    return out


# --------------------------------------------------------------------------- evidence plan

def frame_of(t: float, fps: float) -> int:
    return int(round(t * fps))


def _len(o: Obs) -> float | None:
    if o.extent:
        (x1, y1), (x2, y2) = o.extent
        return math.hypot(x2 - x1, y2 - y1)
    return None


def _nearest(obs: list[Obs], t: float) -> Obs | None:
    return min(obs, key=lambda o: (abs(o.t - t), o.t), default=None)


def _spread_pick(items: list, k: int) -> list:
    if len(items) <= k:
        return list(items)
    idx = sorted(set(np.linspace(0, len(items) - 1, k).round().astype(int).tolist()))
    return [items[i] for i in idx]


def _quantity(q: QCtx, role: str) -> Quantity:
    return q.spec.prior if role.startswith("prior") else q.spec.target


def evidence_obs(track: Track, questions: dict[int, QCtx]) -> list[tuple[Obs, str]]:
    """The obs of a track the evidence shows, with what to check on each ("size", "motion",
    "distance"), most important first: per use, the frames the geometry's value rests on. A size
    read at asked times shows the frame nearest each of them first (each question's own +-0.5 s
    window), then the median-length frame; the cap (SIZE_FRAMES for size-only tracks, MOTION_FRAMES
    otherwise) is raised to keep all asked-time frames plus one."""
    picks: list[tuple[Obs, str]] = []

    def add(o: Obs | None, use: str):
        if o is not None and not any(abs(p.t - o.t) < 1e-6 for p, _ in picks):
            picks.append((o, use))

    sized = [o for o in track.obs if o.extent] or [o for o in track.obs if o.box]
    for u in track.uses:                    # asked-time frames of every size use first
        q = questions.get(u["qid"])
        if q is not None and u["use"] == "size" and sized:
            t = _quantity(q, u["role"]).time
            if t is not None and math.isfinite(t):
                add(_nearest(sized, t), "size")
    n_timed = len(picks)
    for u in track.uses:
        q = questions.get(u["qid"])
        if q is None or u["use"] == "none":
            continue
        quant = _quantity(q, u["role"])
        if u["use"] == "size":
            if not sized:
                continue
            lens = [(_len(o) or max(o.box[2] - o.box[0], o.box[3] - o.box[1])) for o in sized]
            med = float(np.median(lens))
            first = sized[int(np.argmin([abs(x - med) for x in lens]))]
            add(first, "size")
            other = max(sized, key=lambda o: abs(o.t - first.t))
            if other is not first:
                add(other, "size")
        else:
            pts = [o for o in track.obs if o.point is not None or o.box is not None]
            if not pts:
                continue
            times: list[float] = []
            if u["use"] == "distance":
                times = [quant.time] if quant.time is not None else [float(np.median([o.t for o in pts]))]
                times = [min(max(t, pts[0].t), pts[-1].t) if math.isfinite(t) else
                         (pts[-1].t if t > 0 else pts[0].t) for t in times]
            elif quant.window and len(quant.window) == 2:
                t0, t1 = sorted(quant.window)
                times = [t0, t1, (t0 + t1) / 2]
            elif quant.time is not None and math.isfinite(quant.time):
                half = 0.75 if quant.kind == "acceleration" else 0.5
                times = [quant.time, quant.time - half, quant.time + half]
            else:
                times = [pts[0].t, pts[-1].t, pts[len(pts) // 2].t]
            for t in times:
                add(_nearest(pts, t), u["use"])
    cap = SIZE_FRAMES if all(u["use"] == "size" for u in track.uses) else MOTION_FRAMES
    return picks[:max(cap, n_timed + 1, 1)]


@dataclass
class CropSpec:
    frame: int
    x0: int
    y0: int
    x1: int                 # exclusive
    y1: int
    zoom: int
    what: list[str]         # e.g. ["B end 1 (342.0, 190.5)"]


def crop_box(cx: float, cy: float, half: int, W: int, H: int) -> tuple[int, int, int, int]:
    """Integer crop region [x0, x1) x [y0, y1) of side 2*half around (cx, cy), shifted inside the image."""
    side_x, side_y = min(2 * half, W), min(2 * half, H)
    x0 = int(min(max(round(cx - half), 0), W - side_x))
    y0 = int(min(max(round(cy - half), 0), H - side_y))
    return x0, y0, x0 + side_x, y0 + side_y


def crop_geometry(W: int, H: int) -> tuple[int, int]:
    """(half-size in original px, zoom) of endpoint crops for a W x H video: about 12% of the long side
    (56-160 px), zoomed so a crop is ~CROP_OUT_PX wide (2-4x)."""
    half = int(np.clip(round(0.06 * max(W, H)), 28, 80))
    zoom = int(np.clip(CROP_OUT_PX // (2 * half), 2, 4))
    return half, zoom


def plan_evidence(ctx: VideoContext, max_overviews: int = MAX_OVERVIEWS, max_crops: int = MAX_CROPS) -> dict:
    """{"frames": {frame: [(tid, Obs, use), ...]}, "crops": [CropSpec], "per_track": {tid: [frames]}}:
    the evidence frames per track (evidence_obs), capped at max_overviews distinct frames (each
    track's first pick first), and the endpoint / point crops (capped at max_crops)."""
    W, H = ctx.image_size
    half, zoom = crop_geometry(W, H)
    qmap = {q.qid: q for q in ctx.questions}
    picks = {tid: evidence_obs(t, qmap) for tid, t in ctx.tracks.items()}
    order = []
    for k in range(max((len(p) for p in picks.values()), default=0)):   # round-robin: every track gets its first
        for tid, p in picks.items():
            if k < len(p):
                order.append((tid, *p[k]))
    frames: dict[int, list] = {}
    for tid, o, use in order:
        f = frame_of(o.t, ctx.fps)
        if f not in frames and len(frames) >= max_overviews:
            continue
        frames.setdefault(f, []).append((tid, o, use))
    crops: list[CropSpec] = []
    for f in sorted(frames):
        for tid, o, use in frames[f]:
            if use == "size" and o.extent:
                (x1, y1), (x2, y2) = o.extent
                ends = [((x1 + x2) / 2, (y1 + y2) / 2, f"{tid} ends")] if (
                    abs(x2 - x1) <= 1.2 * half and abs(y2 - y1) <= 1.2 * half) else \
                    [(x1, y1, f"{tid} end 1 {_xy_txt((x1, y1))}"), (x2, y2, f"{tid} end 2 {_xy_txt((x2, y2))}")]
                if len(ends) == 1:
                    ends = [(ends[0][0], ends[0][1], f"{tid} end 1 {_xy_txt((x1, y1))}, end 2 {_xy_txt((x2, y2))}")]
            elif use == "size" and o.box:
                bx1, by1, bx2, by2 = o.box
                ends = [((bx1 + bx2) / 2, (by1 + by2) / 2, f"{tid} box")] if (
                    bx2 - bx1 <= 1.2 * half and by2 - by1 <= 1.2 * half) else \
                    [(bx1, by1, f"{tid} box corner {_xy_txt((bx1, by1))}"), (bx2, by2, f"{tid} box corner {_xy_txt((bx2, by2))}")]
            else:
                p = o.point or ([(o.box[0] + o.box[2]) / 2, (o.box[1] + o.box[3]) / 2] if o.box else None)
                if p is None:
                    continue
                ends = [(p[0], p[1], f"{tid} point {_xy_txt(p)}" + ("" if o.point else " (box centre)"))]
            for cx, cy, what in ends:
                if len(crops) >= max_crops:
                    break
                near = next((c for c in crops if c.frame == f and c.x0 + half / 2 <= cx < c.x1 - half / 2
                             and c.y0 + half / 2 <= cy < c.y1 - half / 2), None)
                if near is not None:           # already well inside another crop of this frame
                    near.what.append(what)
                    continue
                x0, y0, x1c, y1c = crop_box(cx, cy, half, W, H)
                crops.append(CropSpec(f, x0, y0, x1c, y1c, zoom, [what]))
    per_track: dict[str, list[int]] = {}
    for f, items in frames.items():
        for tid, _, _ in items:
            per_track.setdefault(tid, []).append(f)
    return {"frames": frames, "crops": crops, "per_track": {k: sorted(v) for k, v in per_track.items()},
            "half": half, "zoom": zoom}


# --------------------------------------------------------------------------- rendering

def _cv(u: float) -> int:
    """Continuous output coordinate (pixel corners at integers) -> cv2 fixed-point (shift 4) at pixel centres."""
    return int(round((u - 0.5) * 16))


def _pt(u: float, v: float) -> tuple[int, int]:
    return _cv(u), _cv(v)


@dataclass
class Canvas:
    """Original-pixel region [x0, x1) x [y0, y1) drawn at `zoom` (scale) with tick-label margins."""
    img: np.ndarray
    x0: float
    y0: float
    zoom: float
    ml: int = MARGIN_L
    mt: int = MARGIN_T

    def to_out(self, x: float, y: float) -> tuple[float, float]:
        """Original continuous coordinates -> continuous canvas coordinates."""
        return self.ml + (x - self.x0) * self.zoom, self.mt + (y - self.y0) * self.zoom

    def to_orig(self, u: float, v: float) -> tuple[float, float]:
        return self.x0 + (u - self.ml) / self.zoom, self.y0 + (v - self.mt) / self.zoom


def make_canvas(region: np.ndarray, x0: float, y0: float, zoom: float) -> Canvas:
    """Resize `region` (pixels [x0, x0+w) x [y0, y0+h) of a frame) by `zoom` (cv2's pixel-centre
    convention: continuous coordinates scale exactly) and pad it with tick-label margins."""
    h, w = region.shape[:2]
    out_w, out_h = int(round(w * zoom)), int(round(h * zoom))
    interp = cv2.INTER_CUBIC if zoom > 1 else cv2.INTER_AREA
    body = cv2.resize(region, (out_w, out_h), interpolation=interp) if (out_w, out_h) != (w, h) else region.copy()
    img = np.full((out_h + MARGIN_T + MARGIN_B, out_w + MARGIN_L + MARGIN_R, 3), 32, np.uint8)
    img[MARGIN_T:MARGIN_T + out_h, MARGIN_L:MARGIN_L + out_w] = body
    return Canvas(img, x0, y0, zoom)


def _tick_step(zoom: float, min_px: float, steps=(1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000)) -> int:
    return next((s for s in steps if s * zoom >= min_px), steps[-1])


_MINOR = {1: 0, 2: 1, 5: 1, 10: 2, 20: 5, 25: 5, 50: 10, 100: 20, 200: 50, 250: 50, 500: 100, 1000: 200}


def draw_ticks(cv: Canvas, w_orig: float, h_orig: float, min_px: float, grid: bool) -> int:
    """Axis ticks on the margins labelled in original pixels (major every `step`, minor ticks), and
    optionally a faint dotted grid at the major ticks. Returns the major step."""
    img, step = cv.img, _tick_step(cv.zoom, min_px)
    minor = _MINOR.get(step, 0)
    top, left = cv.mt, cv.ml
    bottom = cv.mt + int(round(h_orig * cv.zoom))
    right = cv.ml + int(round(w_orig * cv.zoom))
    font = cv2.FONT_HERSHEY_SIMPLEX
    for axis in (0, 1):
        lo, hi = (cv.x0, cv.x0 + w_orig) if axis == 0 else (cv.y0, cv.y0 + h_orig)
        for k, s in ((minor, 3), (step, 7)):
            if not k:
                continue
            v = math.ceil(lo / k) * k
            while v <= hi + 1e-9:
                u = cv.to_out(v, 0)[0] if axis == 0 else cv.to_out(0, v)[1]
                if axis == 0:
                    cv2.line(img, _pt(u, top - s), _pt(u, top), (230, 230, 230), 1, cv2.LINE_AA, 4)
                else:
                    cv2.line(img, _pt(left - s, u), _pt(left, u), (230, 230, 230), 1, cv2.LINE_AA, 4)
                if k == step:
                    label = f"{v:g}"
                    if axis == 0:
                        (tw, _), _ = cv2.getTextSize(label, font, 0.38, 1)
                        cv2.putText(img, label, (int(u - tw / 2), top - 9), font, 0.38, (230, 230, 230), 1, cv2.LINE_AA)
                    else:
                        (tw, th), _ = cv2.getTextSize(label, font, 0.38, 1)
                        cv2.putText(img, label, (left - 9 - tw, int(u + th / 2)), font, 0.38, (230, 230, 230), 1,
                                    cv2.LINE_AA)
                    if grid:
                        if axis == 0:
                            for yy in range(top, bottom, 6):
                                _blend_px(img, int(u), yy)
                        else:
                            for xx in range(left, right, 6):
                                _blend_px(img, xx, int(u))
                v += k
    return step


def finish(cv: Canvas, w_orig: float, h_orig: float, min_px: float, grid: bool) -> None:
    """Clear the margins (marks drawn past the image edge) and draw the ticks: call after the marks."""
    out_w, out_h = int(round(w_orig * cv.zoom)), int(round(h_orig * cv.zoom))
    img = cv.img
    img[:cv.mt] = 32
    img[cv.mt + out_h:] = 32
    img[:, :cv.ml] = 32
    img[:, cv.ml + out_w:] = 32
    draw_ticks(cv, w_orig, h_orig, min_px, grid)


def _blend_px(img: np.ndarray, x: int, y: int, a: float = 0.45) -> None:
    if 0 <= y < img.shape[0] and 0 <= x < img.shape[1]:
        img[y, x] = (img[y, x] * (1 - a) + np.array([255, 255, 255]) * a).astype(np.uint8)


def _text(img, s: str, u: float, v: float, color, scale: float = 0.42) -> None:
    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (int(u), int(v))
    cv2.putText(img, s, org, font, scale, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(img, s, org, font, scale, color, 1, cv2.LINE_AA)


def draw_cross(cv: Canvas, x: float, y: float, color, arm: float = 9, gap: float = 3, thick: int = 1,
               ring: float = 0.0) -> None:
    """Cross-hair centred on the original point (x, y), open in the middle so the pixel stays visible
    (arms from `gap` to `arm` canvas px; optionally a ring of radius `ring` around the centre)."""
    u, v = cv.to_out(x, y)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        cv2.line(cv.img, _pt(u + dx * gap, v + dy * gap), _pt(u + dx * arm, v + dy * arm), color, thick,
                 cv2.LINE_AA, 4)
    if ring:
        cv2.circle(cv.img, _pt(u, v), int(round(ring * 16)), color, thick, cv2.LINE_AA, 4)


def draw_segment(cv: Canvas, a, b, color, stop: float = 0.0, dashed: bool = False, thick: int = 1) -> None:
    """Segment between original points a and b, stopped `stop` canvas px short of each end."""
    ua, va = cv.to_out(*a)
    ub, vb = cv.to_out(*b)
    d = math.hypot(ub - ua, vb - va)
    if d <= 2 * stop + 1:
        return
    ex, ey = (ub - ua) / d, (vb - va) / d
    ua, va, ub, vb = ua + ex * stop, va + ey * stop, ub - ex * stop, vb - ey * stop
    if not dashed:
        cv2.line(cv.img, _pt(ua, va), _pt(ub, vb), color, thick, cv2.LINE_AA, 4)
        return
    n = max(1, int((d - 2 * stop) // 8))
    for i in range(0, n, 2):
        s0, s1 = i / n, min((i + 1) / n, 1)
        cv2.line(cv.img, _pt(ua + (ub - ua) * s0, va + (vb - va) * s0), _pt(ua + (ub - ua) * s1, va + (vb - va) * s1),
                 color, thick, cv2.LINE_AA, 4)


def draw_box(cv: Canvas, box, color, thick: int = 1, corners: float = 0.0) -> None:
    """Box outline; with `corners` > 0 only corner brackets of that many canvas px per arm (at most a
    third of the side), so the sides themselves (object edges) stay visible."""
    x1, y1, x2, y2 = box
    if not corners:
        for a, b in (((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)), ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))):
            draw_segment(cv, a, b, color, thick=thick)
        return
    ax = min(corners / cv.zoom, abs(x2 - x1) / 3)
    ay = min(corners / cv.zoom, abs(y2 - y1) / 3)
    for cx, sx in ((x1, 1), (x2, -1)):
        for cy, sy in ((y1, 1), (y2, -1)):
            draw_segment(cv, (cx, cy), (cx + sx * ax, cy), color, thick=thick)
            draw_segment(cv, (cx, cy), (cx, cy + sy * ay), color, thick=thick)


def box_is_read(o: Obs, use: str) -> bool:
    """Whether the geometry reads this obs's box: a size without an extent, a point without a point."""
    return bool(o.box) and ((use == "size" and not o.extent) or (use != "size" and o.point is None))


def _color(ctx_tids: list[str], tid: str) -> tuple[str, tuple]:
    return PALETTE[ctx_tids.index(tid) % len(PALETTE)]


def render_overview(img: np.ndarray, frame: int, items: list, ctx: VideoContext, max_side: int = MAX_SIDE) -> tuple[np.ndarray, dict]:
    """Full frame (downscaled to max_side) with every evidence mark of this frame: extents (segment +
    endpoint circles), boxes, motion paths with timestamps (the current point as a cross-hair) and
    distances (dashed). Returns (image, info with the scale)."""
    H, W = img.shape[:2]
    s = min(1.0, max_side / max(W, H))
    cv = make_canvas(img, 0, 0, s)
    tids = list(ctx.tracks)
    drawn_paths = set()
    for tid, o, use in items:
        name, col = _color(tids, tid)
        tr = ctx.tracks[tid]
        if use == "motion" and tid not in drawn_paths:
            drawn_paths.add(tid)
            pts = [p for p in tr.obs if p.point is not None]
            for a, b in zip(pts, pts[1:]):
                draw_segment(cv, a.point, b.point, col)
            labelled: list[tuple[float, float]] = []
            for p in _spread_pick(pts, 6):
                u, v = cv.to_out(*p.point)
                cv2.circle(cv.img, _pt(u, v), 2 * 16, col, -1, cv2.LINE_AA, 4)
                if all(math.hypot(u - a, v - b) >= 40 for a, b in labelled):
                    labelled.append((u, v))
                    _text(cv.img, f"{p.t:.2f}s", u + 4, v - 4, col, 0.35)
        if o.box and not (use == "size" and o.extent):
            draw_box(cv, o.box, col)
        if o.extent:
            (a, b) = o.extent
            draw_segment(cv, a, b, col, thick=1)
            for p in (a, b):
                u, v = cv.to_out(*p)
                cv2.circle(cv.img, _pt(u, v), 4 * 16, col, 1, cv2.LINE_AA, 4)
            mu, mv = cv.to_out((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            _text(cv.img, tid, mu + 6, mv - 6, col)
        p = o.point or ([(o.box[0] + o.box[2]) / 2, (o.box[1] + o.box[3]) / 2] if o.box and use != "size" else None)
        if p is not None and use != "size":
            draw_cross(cv, p[0], p[1], col, arm=10, gap=3)
            u, v = cv.to_out(*p)
            _text(cv.img, tid, u + 7, v + 14, col)
    for q in ctx.questions:    # distances between two tracks on this frame: dashed
        roles = dict((r, t) for r, t in q.roles)
        for a_role, b_role, quant in (("target", "target2", q.spec.target), ("prior", "prior2", q.spec.prior)):
            if quant.kind != "distance" or a_role not in roles or b_role not in roles:
                continue
            pa = next((o for t, o, _ in items if t == roles[a_role]), None)
            pb = next((o for t, o, _ in items if t == roles[b_role]), None)
            ca_ = pa and (pa.point or (pa.box and [(pa.box[0] + pa.box[2]) / 2, (pa.box[1] + pa.box[3]) / 2]))
            cb_ = pb and (pb.point or (pb.box and [(pb.box[0] + pb.box[2]) / 2, (pb.box[1] + pb.box[3]) / 2]))
            if ca_ and cb_:
                draw_segment(cv, ca_, cb_, (255, 255, 255), stop=4, dashed=True)
    finish(cv, W, H, 60, grid=False)
    return cv.img, {"scale": s}


def render_crop(img: np.ndarray, crop: CropSpec, items: list, ctx: VideoContext) -> np.ndarray:
    """Zoomed crop with tick labels in original pixels and the marks of this frame inside it, drawn thin
    and open in the middle (cross-hairs) so the measured pixel itself stays visible. A box is drawn only
    when the geometry reads it (box_is_read), and then as corner brackets, never as full sides."""
    region = img[crop.y0:crop.y1, crop.x0:crop.x1]
    cv = make_canvas(region, crop.x0, crop.y0, crop.zoom)
    tids = list(ctx.tracks)
    for tid, o, use in items:
        _, col = _color(tids, tid)
        if box_is_read(o, use):     # other boxes would run along object edges, where endpoints are judged
            draw_box(cv, o.box, col, corners=12)
        if o.extent:
            a, b = o.extent
            draw_segment(cv, a, b, col, stop=8)
            for k, p in enumerate((a, b), 1):
                draw_cross(cv, p[0], p[1], col, arm=14, gap=7, ring=5)
                u, v = cv.to_out(*p)
                _text(cv.img, f"{tid}{k}", u + 8, v - 8, col)
        p = o.point or ([(o.box[0] + o.box[2]) / 2, (o.box[1] + o.box[3]) / 2] if o.box and use != "size" else None)
        if p is not None:
            draw_cross(cv, p[0], p[1], col, arm=14, gap=7, ring=5)
            u, v = cv.to_out(*p)
            _text(cv.img, tid, u + 8, v - 8, col)
    finish(cv, crop.x1 - crop.x0, crop.y1 - crop.y0, 36, grid=True)
    return cv.img


def read_frames_raw(path: str, indices: list[int]) -> dict[int, np.ndarray]:
    """BGR frames at the given indices (sequential decode: exact for any codec)."""
    want, out = set(int(i) for i in indices), {}
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise FileNotFoundError(path)
    i = 0
    hi = max(want) if want else -1
    while i <= hi and cap.grab():
        if i in want:
            ok, img = cap.retrieve()
            if ok:
                out[i] = img
        i += 1
    cap.release()
    return out


def _jpeg(img: np.ndarray, quality: int = JPEG_QUALITY) -> str:
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise RuntimeError("jpeg encode failed")
    return base64.b64encode(buf).decode()


def render_evidence(ctx: VideoContext, plan: dict, max_side: int = MAX_SIDE, frames: dict | None = None) -> list[dict]:
    """[{"iid", "kind": "frame"|"crop", "frame", "t", "region": [x0, y0, x1, y1], "zoom", "what",
    "jpeg_b64", "width", "height"}] in prompt order: per frame, the full view then its crops."""
    want = sorted(plan["frames"])
    frames = frames if frames is not None else read_frames_raw(ctx.video_path, want)
    W, H = ctx.image_size
    out: list[dict] = []
    for f in want:
        img = frames.get(f)
        if img is None:
            continue
        if (img.shape[1], img.shape[0]) != (W, H):     # pass-1 coordinates are in the original size
            img = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)
        items = plan["frames"][f]
        ov, info = render_overview(img, f, items, ctx, max_side)
        marks = []
        for tid, o, use in items:
            name = _color(list(ctx.tracks), tid)[0]
            if use == "size" and o.extent:
                marks.append(f"{tid} ({name}) extent {_xy_txt(o.extent[0])}-{_xy_txt(o.extent[1])}, "
                             f"{_len(o):.1f} px")
            elif use == "size" and o.box:
                marks.append(f"{tid} ({name}) box {[_r(v) for v in o.box]}")
            else:
                p = o.point or [(o.box[0] + o.box[2]) / 2, (o.box[1] + o.box[3]) / 2]
                marks.append(f"{tid} ({name}) point {_xy_txt(p)}" + (" with its path" if use == "motion" else ""))
        out.append({"kind": "frame", "frame": f, "t": f / ctx.fps, "region": [0, 0, W, H], "zoom": info["scale"],
                    "what": marks, "jpeg_b64": _jpeg(ov), "width": ov.shape[1], "height": ov.shape[0]})
        for c in plan["crops"]:
            if c.frame != f:
                continue
            inside = [(tid, o, use) for tid, o, use in items]
            im = render_crop(img, c, inside, ctx)
            out.append({"kind": "crop", "frame": f, "t": f / ctx.fps, "region": [c.x0, c.y0, c.x1, c.y1],
                        "zoom": c.zoom, "what": list(c.what), "jpeg_b64": _jpeg(im), "width": im.shape[1],
                        "height": im.shape[0]})
    for k, e in enumerate(out, 1):
        e["iid"] = k
    return out


# --------------------------------------------------------------------------- request

_NUM_OR_NULL = {"anyOf": [{"type": "number"}, {"type": "null"}]}
_OBS = ca._OBS
_TRACK_FIX = {
    "type": "object",
    "properties": {"track": {"type": "string"}, "action": {"type": "string", "enum": list(ACTIONS)},
                   "problem": {"type": "string"},
                   "depth_name": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                   "obs": {"type": "array", "items": _OBS}},
    "required": ["track", "action", "problem", "depth_name", "obs"],
    "additionalProperties": False,
}
_QFIX = {
    "type": "object",
    "properties": {"change": {"type": "array", "items": {"type": "string", "enum": list(SPEC_FIELDS)}},
                   "kind": {"anyOf": [{"type": "string", "enum": list(KINDS)}, {"type": "null"}]},
                   "objects": {"anyOf": [{"type": "array", "items": {"type": "string"}}, {"type": "null"}]},
                   "dimension": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                   "time": _NUM_OR_NULL,
                   "window": {"anyOf": [{"type": "array", "items": {"type": "number"}}, {"type": "null"}]},
                   "axis": {"anyOf": [{"type": "string", "enum": list(ca.AXES)}, {"type": "null"}]}},
    "required": ["change", "kind", "objects", "dimension", "time", "window", "axis"],
    "additionalProperties": False,
}
_QVERIFY = {
    "type": "object",
    "properties": {"qid": {"type": "integer"}, "verdict": {"type": "string", "enum": list(VERDICTS)},
                   "problem": {"type": "string"},
                   "spec_fix": {"type": "object", "properties": {"target": _QFIX, "prior": _QFIX},
                                "required": ["target", "prior"], "additionalProperties": False},
                   "final_answer": {"type": "number"}, "confidence": {"type": "number"}},
    "required": ["qid", "verdict", "problem", "spec_fix", "final_answer", "confidence"],
    "additionalProperties": False,
}
SCHEMA = {
    "type": "object",
    "properties": {"tracks": {"type": "array", "items": _TRACK_FIX}, "questions": {"type": "array", "items": _QVERIFY}},
    "required": ["tracks", "questions"],
    "additionalProperties": False,
}

COORDS = f"""\
Coordinates: always ORIGINAL video pixels, x right, y down, origin at the top-left corner of the frame. \
Full frames may be downscaled and crops are zoomed. Every image has a dark tick band of {MARGIN_L} px on \
the left and {MARGIN_T} px on top before the picture starts ({MARGIN_R} px on the right and bottom); the \
tick labels on those bands are original-pixel coordinates. Read corrected positions from the tick labels, to \
0.5 px. Equivalently, the text line before each image gives its region (x0, y0) and zoom (crop) or scale \
(full frame), and a position (u, v) in that image's own pixels (counted from the image's top-left \
corner, tick band included) is original x = x0 + (u - {MARGIN_L}) / zoom, y = y0 + (v - {MARGIN_T}) / zoom \
(full frames: x0 = y0 = 0 and zoom = scale). Never give image pixels as coordinates."""

SYSTEM_VF1 = """\
You are the verification stage of a measurement pipeline for QuantiPhy, a benchmark of quantitative \
physical reasoning from video. Each question gives one known physical quantity of the video (the prior), \
sometimes object-to-camera distances (depth info, 3D videos), and asks for another quantity. A first pass \
annotated ONE video: per question it parsed a spec (what to measure), placed pixel measurements on the \
frames (tracks), and a geometry program computed the answer = (metric scale from the prior) x (pixel \
measurement of the target); 3D videos use a pinhole camera, the depth info and a focal length. Answers \
score only when within a few percent, so a few pixels matter: your job is to find and fix the \
measurement and spec errors behind the answers.

What you get
- Tracks, with ids A, B, ... and a colour: the object, its coordinates per frame and what the geometry \
reads from it (a size from extent endpoints, motion from points over time, a distance from points at one \
time). A track can serve several questions; a correction applies to all of them.
- Evidence images, each preceded by a text line: full frames with the measurements drawn (extents as a \
segment with circled endpoints, boxes, a motion track's whole path with timestamps and the point of \
that frame as a cross-hair, a distance as a dashed line), and zoomed crops around every measured \
endpoint / point, where each mark is an open cross-hair centred on the measured position (the pixel \
itself stays visible) labelled with the track id (B1 / B2 = the two extent ends).
- Per question: the question and prior text, the parsed spec, the measured pixel quantities, the scale \
(2D: metres per pixel) or focal length and ranges (3D), the geometry answer and the first pass's own \
direct estimate.

{COORDS}

How to check
1. Tracks: right object (the one the question names; the same instance on every frame)? Extent \
endpoints exactly on the object's physical ends along the asked dimension (not on a shadow, reflection, \
motion blur, background, nor short of the true end)? The right dimension (length / height / width / \
diameter / wingspan as asked) and not foreshortened? Motion points on the same physical point of the \
object on every frame, and on the right object? A box tight?
2. Specs against the question and prior text: kind, objects, dimension, time, window, axis.
3. 3D: is the depth-info entry matched to each object the right one?
Fix only what you can see is wrong; keep what is right. Do not move a point by less than 1 px, and do \
not replace a measurement you cannot place better than the first pass did. A track marked "refined by \
optical flow" follows its point to sub-pixel accuracy from frame to frame: replace it only when it \
follows the wrong object or drifts off it. The first pass's direct estimate rests on the same \
measurements as its geometry answer, so agreement between the two proves nothing.

Output
- tracks: one entry per track id. action "keep" with obs [] when the track is right. action "replace": \
your obs replace the track's on their frames and its other frames get the same change (a track used \
for motion becomes exactly your obs); give obs on frames shown in the evidence images only (use those \
frame indices): for a size the corrected extent (both endpoints, plus the box if easy) on every evidence \
frame of that track where the dimension is fully visible; for motion or a distance the corrected point \
(the same physical point each time; the box where easy) on every evidence frame of that track. Null \
fields you do not give. problem: what was wrong, in a few words ("" if nothing). depth_name: for 3D, \
the depth-info object name this track's object is when the matched entry is wrong, else null.
- questions: one entry per qid. verdict "accept_geometry" (spec and measurements right), "corrected" \
(you replaced a track this question uses or fix its spec: the program recomputes the geometry from \
your coordinates, so the coordinates must be right; your own arithmetic is not used), or \
"accept_direct" (the geometry is wrong in a way coordinates cannot fix, e.g. the measured object is not \
in any evidence image, and the first pass's direct estimate is better). spec_fix: for target and prior, \
"change" lists the fields to change (others are ignored; [] = no change) and those fields carry the new \
values (time and window in seconds; window [t0, t1]). final_answer: your best estimate in the asked unit \
after your corrections, a positive number. confidence: 0-1 that final_answer is within 5%.
Answer every track and every question."""

SYSTEM = """\
You are the verification stage of a measurement pipeline for QuantiPhy, a benchmark of quantitative \
physical reasoning from video. Each question gives one known physical quantity of the video (the prior), \
sometimes object-to-camera distances (depth info, 3D videos), and asks for another quantity. A first pass \
annotated ONE video: per question it parsed a spec (what to measure), placed pixel measurements on the \
frames (tracks), and a geometry program computed the answer = (metric scale from the prior) x (pixel \
measurement of the target); 3D videos use a pinhole camera, the depth info and a focal length. Answers \
score only when within a few percent, so a few pixels matter: your job is to find and fix the \
measurement and spec errors behind the answers.

What you get
- Tracks, with ids A, B, ... and a colour: the object, its coordinates per frame and what the geometry \
reads from it (a size from extent endpoints, motion from points over time, a distance from points at one \
time). A track can serve several questions; a correction applies to all of them.
- Evidence images, each preceded by a text line: full frames with the measurements drawn (extents as a \
segment with circled endpoints, boxes, a motion track's whole path with timestamps and the point of \
that frame as a cross-hair, a distance as a dashed line), and zoomed crops around every measured \
endpoint / point, where each mark is an open cross-hair centred on the measured position (the pixel \
itself stays visible) labelled with the track id (B1 / B2 = the two extent ends).
- Per question: the question and prior text, the parsed spec, the measured pixel quantities, the scale \
(2D: metres per pixel) or focal length and ranges (3D), the geometry answer and the first pass's own \
direct estimate.

{COORDS}

How to check
1. Tracks: right object (the one the question names; the same instance on every frame)? Extent \
endpoints exactly on the object's physical ends along the asked dimension (not on a shadow, reflection, \
motion blur, background, nor short of the true end)? The right dimension (length / height / width / \
diameter / wingspan as asked) and not foreshortened? Motion points on the same physical point of the \
object on every frame, and on the right object? A box tight?
2. Specs against the question and prior text: kind, objects, dimension, time, window, axis.
3. 3D: is the depth-info entry matched to each object the right one?
Fix only what you can see is wrong; keep what is right. Do not move a point by less than 1 px, and do \
not replace a measurement you cannot place better than the first pass did. A track marked "refined by \
optical flow" follows its point to sub-pixel accuracy from frame to frame: replace it only when it \
follows the wrong object or drifts off it. The first pass's direct estimate rests on the same \
measurements as its geometry answer, so agreement between the two proves nothing.

Output
- tracks: one entry per track id. obs: ALWAYS your own reading of the track on every evidence frame of \
that track (the frames whose images show it; use those frame indices only): for a size both extent \
endpoints, for motion or a distance the point (the same physical point each time), plus the box where \
easy; null for fields you do not give. Read each position from the zoomed crop's tick labels to 0.5 px, \
at the object's true end / point, not at the first pass's mark. action "keep" when your reading \
agrees with the first pass within about 1 px or you cannot place it better; "replace" when the first \
pass is wrong (wrong position, object, instance or dimension): your obs then replace the first pass's \
on those frames and its other frames get the same change (sizes scaled by your length / its length, \
points shifted by your offset); a track used for motion becomes exactly your obs. For a size give only \
frames where the dimension is fully visible. problem: what was wrong, in a few words \
("" if nothing). depth_name: for 3D, the depth-info object name this track's object is when the matched \
entry is wrong, else null.
- questions: one entry per qid. verdict "accept_geometry" (spec and measurements right), "corrected" \
(you replaced a track this question uses or fix its spec: the program recomputes the geometry from \
your coordinates, so the coordinates must be right; your own arithmetic is not used), or \
"accept_direct" (the geometry is wrong in a way coordinates cannot fix, e.g. the measured object is not \
in any evidence image, and the first pass's direct estimate is better). spec_fix: for target and prior, \
"change" lists the fields to change (others are ignored; [] = no change) and those fields carry the new \
values (time and window in seconds; window [t0, t1]). final_answer: your best estimate in the asked unit \
after your corrections, a positive number. confidence: 0-1 that final_answer is within 5%.
Answer every track and every question."""
SYSTEM_VF1 = SYSTEM_VF1.replace("{COORDS}", COORDS)
SYSTEM = SYSTEM.replace("{COORDS}", COORDS)
SYSTEMS = {"vf1": SYSTEM_VF1, "vf2": SYSTEM}   # vf1: obs only with "replace"; vf2: every track carries
# the model's own reading (module docstring)


def _quantity_txt(q: Quantity, who: str) -> str:
    bits = [f"kind={q.kind}", f"objects={q.objects}"]
    if q.dimension:
        bits.append(f"dimension={q.dimension}")
    if q.time is not None:
        bits.append(f"time={q.time:g}s")
    if q.window:
        bits.append(f"window=[{q.window[0]:g}, {q.window[1]:g}]s")
    if q.axis and q.axis != "any":
        bits.append(f"axis={q.axis}")
    if who == "prior" and q.value_si is not None:
        bits.append(f"value={q.value_si:g} SI")
    if who == "target" and q.unit:
        bits.append(f"unit={q.unit}")
    return ", ".join(bits)


def _obs_txt(o: Obs, fps: float) -> str:
    f = frame_of(o.t, fps)
    parts = [f"frame {f} (t={o.t:.3f}s)"]
    if o.point is not None:
        parts.append(f"point {_xy_txt(o.point)}")
    if o.extent is not None:
        parts.append(f"extent {_xy_txt(o.extent[0])}-{_xy_txt(o.extent[1])} = {_len(o):.1f} px")
    if o.box is not None:
        parts.append(f"box [{', '.join(f'{v:.1f}' for v in o.box)}]")
    return " ".join(parts)


def _track_txt(t: Track, ctx: VideoContext, plan: dict) -> str:
    name = _color(list(ctx.tracks), t.tid)[0]
    uses = "; ".join(f"{u['use']} for qid {u['qid']} {u['role']}" for u in t.uses) or "unused"
    head = f"Track {t.tid} ({name}): \"{t.object}\" - used as {uses}."
    if t.depth_name:
        head += f" Linked depth entry: {t.depth_name}."
    if t.range_m:
        head += f" First-pass range estimate {t.range_m:g} m."
    if not t.obs:
        return head + " No observations."
    ev = set(plan["per_track"].get(t.tid, []))
    if t.refined:
        head += f" Points refined by optical flow: one per frame, {len(t.obs)} obs from frame " \
                f"{frame_of(t.obs[0].t, ctx.fps)} to {frame_of(t.obs[-1].t, ctx.fps)}."
    shown = t.obs if len(t.obs) <= LIST_OBS else [o for o in t.obs if frame_of(o.t, ctx.fps) in ev]
    lines = [head]
    if len(shown) < len(t.obs):
        lines.append(f"  ({len(t.obs)} obs; listed: those on evidence frames)")
    lines += [f"  {_obs_txt(o, ctx.fps)}" + ("  [evidence]" if frame_of(o.t, ctx.fps) in ev else "") for o in shown]
    if not ev:
        lines.append("  (no evidence images for this track)")
    return "\n".join(lines)


def _geo_txt(q: QCtx, geo: Answer, ctx: VideoContext) -> str:
    d = geo.debug
    unit = q.spec.target.unit or "SI"
    lines = []
    if "prior_px" in d:
        dim = KIND_DIM.get(q.spec.prior.kind, "L")
        u = {"L": "px", "V": "px/s", "A": "px/s^2"}[dim]
        lines.append(f"prior measured {d['prior_px']:.4g} {u}; scale {d['scale_m_per_px']:.5g} m/px")
    if "f_px" in d:
        lines.append(f"focal length {d['f_px']:.4g} px (horizontal FOV {d.get('fov_deg', float('nan')):.1f} deg)"
                     + (f"; prior re-measured {d['prior_measured_si']:.4g} SI" if "prior_measured_si" in d else ""))
        rng = ", ".join(f"{k[6:-2]} {v:.3g} m" for k, v in d.items() if k.startswith("range_") and k.endswith("_m"))
        if rng:
            lines.append(f"ranges used: {rng}")
        dep = ", ".join(f"{k[6:]} -> {v}" for k, v in d.items() if k.startswith("depth_"))
        if dep:
            lines.append(f"depth entries matched: {dep}")
    if "target_px" in d:
        dim = KIND_DIM.get(q.spec.target.kind, "L")
        u = {"L": "px", "V": "px/s", "A": "px/s^2"}[dim]
        lines.append(f"target measured {d['target_px']:.4g} {u}")
    if "target_measured_si" in d:
        lines.append(f"target {d['target_measured_si']:.4g} SI")
    val = f"{geo.value:.4g} {unit}" if valid(geo.value) else "none"
    flags = [f for f in geo.flags if f not in ("f_camera_prior",)]
    lines.append(f"geometry answer: {val} ({geo.method or 'unsolved'}{'; flags ' + ', '.join(flags) if flags else ''})")
    return "\n  ".join(lines)


def question_txt(q: QCtx, ctx: VideoContext, geo: Answer, chosen: tuple) -> str:
    roles = ", ".join(f"{r} = track {t}" for r, t in q.roles) or "no tracks"
    depth = q.depth_info.strip() or "none (2D video)"
    direct = f"{q.direct:.4g}" if valid(q.direct) else "none"
    lines = [f"Question qid={q.qid}",
             f"Prior: {q.prior_text.strip()}",
             f"Depth info: {depth}",
             f"Question: {q.question.strip()}",
             f"Spec: target {_quantity_txt(q.spec.target, 'target')}",
             f"      prior {_quantity_txt(q.spec.prior, 'prior')}",
             f"Tracks: {roles}",
             "Measurement:\n  " + _geo_txt(q, geo, ctx),
             f"First-pass direct estimate: {direct}; answer currently used: "
             f"{chosen[0]:.4g} ({chosen[1]})" if valid(chosen[0]) else f"First-pass direct estimate: {direct}"]
    if q.dense_value is not None:
        lines.append(f"Dense-tracking answer: {q.dense_value:.4g}")
    if q.spec.notes:
        lines.append(f"First-pass notes: {q.spec.notes}")
    return "\n".join(lines)


def default_max_tokens(n_questions: int, n_tracks: int = 0) -> int:
    return int(min(64000, 8000 + 3000 * n_questions + 600 * n_tracks))


def pass1_answers(ctx: VideoContext, rule: str = combine.DEFAULT_RULE) -> dict[int, dict]:
    """{qid: {"geo": Answer, "chosen": (value, how, flags)}} of the pass-1 tracks and specs."""
    out = {}
    for q in ctx.questions:
        geo = solve_question(q.spec, role_tracks(q, ctx.tracks), ctx.image_size, ctx.fps, ctx.video_source)
        out[q.qid] = {"geo": geo, "chosen": select(geo, q.direct, q.ann_flags, q.spec, ctx.video_source, rule)}
    return out


def build_request(ctx: VideoContext, effort: str = "high", max_tokens: int = 0, model: str = MODEL,
                  max_side: int = MAX_SIDE, max_overviews: int = MAX_OVERVIEWS, max_crops: int = MAX_CROPS,
                  frames: dict | None = None, rule: str = combine.DEFAULT_RULE,
                  version: str = VERIFY_VERSION) -> tuple[dict, dict]:
    """Messages API params and the metadata `recompute` needs (tracks, specs, evidence transforms).
    version: the request version (SYSTEMS)."""
    if version not in SYSTEMS:
        raise ValueError(f"unknown verify version {version!r} (expected one of {tuple(SYSTEMS)})")
    plan = plan_evidence(ctx, max_overviews, max_crops)
    ev = render_evidence(ctx, plan, max_side, frames)
    p1 = pass1_answers(ctx, rule)
    W, H = ctx.image_size
    is_3d = ctx.is_3d
    content: list[dict] = [{"type": "text", "text": (
        f"Video {ctx.video_id}: {'3D video with camera distances' if is_3d else '2D video'}; original size "
        f"{W}x{H} px; {ctx.fps:g} fps; {ctx.n_frames} frames (~{ctx.n_frames / ctx.fps:.2f} s); "
        f"{len(ctx.questions)} question(s), {len(ctx.tracks)} track(s), {len(ev)} evidence images.")}]
    content.append({"type": "text", "text": "TRACKS\n" + "\n".join(
        _track_txt(t, ctx, plan) for t in ctx.tracks.values())})
    for e in ev:
        x0, y0, x1, y1 = e["region"]
        if e["kind"] == "frame":
            label = (f"[Image {e['iid']}] frame {e['frame']} (t={e['t']:.3f}s), full frame "
                     f"x {x0}-{x1}, y {y0}-{y1}, shown at scale {e['zoom']:.6g} (original x = (u - {MARGIN_L}) / "
                     f"{e['zoom']:.6g}, y = (v - {MARGIN_T}) / {e['zoom']:.6g} for image pixel (u, v)). Marks: "
                     + "; ".join(e["what"]))
        else:
            label = (f"[Image {e['iid']}] crop of frame {e['frame']} (t={e['t']:.3f}s): original x {x0}-{x1}, "
                     f"y {y0}-{y1}, zoom {e['zoom']}x (original x = {x0} + (u - {MARGIN_L}) / {e['zoom']}, "
                     f"y = {y0} + (v - {MARGIN_T}) / {e['zoom']} for image pixel (u, v)). "
                     f"Shows: " + "; ".join(e["what"]))
        content.append({"type": "text", "text": label})
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": e["jpeg_b64"]}})
    shown = sorted({e["frame"] for e in ev})
    content.append({"type": "text", "text": (
        f"QUESTIONS ({len(ctx.questions)})\n\n" + "\n\n".join(
            question_txt(q, ctx, p1[q.qid]["geo"], p1[q.qid]["chosen"]) for q in ctx.questions)
        + f"\n\nFrames you may use in replaced tracks: {shown}. Answer every track ({', '.join(ctx.tracks)}) "
          f"and every question ({', '.join(str(q.qid) for q in ctx.questions)}).")})
    params = {
        "model": model,
        "max_tokens": max_tokens or default_max_tokens(len(ctx.questions), len(ctx.tracks)),
        "system": [{"type": "text", "text": SYSTEMS[version], "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": content}],
        "output_config": {"effort": effort, "format": {"type": "json_schema", "schema": SCHEMA}},
    }
    meta = context_meta(ctx)
    meta.update({"evidence": [{k: v for k, v in e.items() if k != "jpeg_b64"} for e in ev], "frames_shown": shown,
                 "pass1": {str(q): {"geo_value": a["geo"].value, "geo_method": a["geo"].method,
                                    "value": a["chosen"][0], "how": a["chosen"][1]} for q, a in p1.items()},
                 "verify_version": version})
    return params, meta


def context_meta(ctx: VideoContext) -> dict:
    """JSON-serialisable VideoContext (what the verifier saw: recompute works from this alone)."""
    return {"video_id": ctx.video_id, "video_path": ctx.video_path, "fps": ctx.fps,
            "image_size": list(ctx.image_size), "n_frames_total": ctx.n_frames, "video_type": ctx.video_type,
            "video_source": ctx.video_source, "tracks": {k: t.to_dict() for k, t in ctx.tracks.items()},
            "questions": [{"qid": q.qid, "question": q.question, "prior": q.prior_text, "depth_info": q.depth_info,
                           "category": q.category, "spec": q.spec.to_dict(), "roles": q.roles, "direct": q.direct,
                           "confidence": q.confidence, "ann_flags": q.ann_flags, "dense_value": q.dense_value}
                          for q in ctx.questions]}


def context_from_meta(meta: dict) -> VideoContext:
    qs = [QCtx(qid=int(q["qid"]), question=q["question"], prior_text=q["prior"], depth_info=q["depth_info"],
               category=q.get("category", ""), spec=QuestionSpec.from_dict(q["spec"]), roles=[list(r) for r in q["roles"]],
               direct=q.get("direct"), confidence=q.get("confidence"), ann_flags=list(q.get("ann_flags") or []),
               dense_value=q.get("dense_value")) for q in meta["questions"]]
    return VideoContext(video_id=meta["video_id"], video_path=meta.get("video_path", ""), fps=float(meta["fps"]),
                        image_size=tuple(meta["image_size"]), n_frames=int(meta.get("n_frames_total") or 0),
                        video_type=meta["video_type"], video_source=meta.get("video_source", ""),
                        tracks={k: Track.from_dict(t) for k, t in meta["tracks"].items()}, questions=qs)


# --------------------------------------------------------------------------- response -> answers

def _xy(p):
    return ca._xy(p)


def parse_obs(o: dict, fps: float, shown: set[int], W: int, H: int, flags: list[str]) -> Obs | None:
    """One corrected obs in original pixels; None (with a flag) for frames not shown, bad shapes or
    coordinates outside the frame (beyond 5% of its size)."""
    f = o.get("frame")
    if not isinstance(f, int) or f not in shown:
        flags.append("verify_unknown_frame")
        return None
    pad_x, pad_y = 0.05 * W, 0.05 * H
    inside = lambda p: -pad_x <= p[0] <= W + pad_x and -pad_y <= p[1] <= H + pad_y  # noqa: E731
    point = _xy(o.get("point"))
    ext = o.get("extent")
    extent = [_xy(ext[0]), _xy(ext[1])] if isinstance(ext, list) and len(ext) == 2 else None
    extent = extent if extent and all(extent) else None
    box = o.get("box")
    box = [float(v) for v in box] if isinstance(box, list) and len(box) == 4 and all(
        ca._num(v) is not None for v in box) else None
    if box:
        box = [min(box[0], box[2]), min(box[1], box[3]), max(box[0], box[2]), max(box[1], box[3])]
    pts = ([point] if point else []) + (extent or []) + ([box[:2], box[2:]] if box else [])
    if not pts:
        return None
    if not all(inside(p) for p in pts):
        flags.append("verify_outside_frame")
        return None
    return Obs(t=f / fps, point=point, extent=extent, box=box)


FIELDS = ("point", "extent", "box")
SPACE_MIN_PX = 4.0        # pixel-space check: readings this close to pass 1 are never suspect
SPACE_TOL_PX = 2.0        # ... else suspect within max(this, 1/4 of its move) of an image-pixel mapping
NOOP_PX = 1.0             # a motion track "replaced" by readings all this close to pass 1 is kept


def _frames(obs: list[Obs], fps: float) -> dict[int, list[Obs]]:
    out: dict[int, list[Obs]] = {}
    for o in obs:
        out.setdefault(frame_of(o.t, fps), []).append(o)
    return out


def _first_with(obs: list[Obs], name: str) -> Obs | None:
    """The first obs of a frame that has field `name` (refined tracks repeat frames: point obs, then
    box-only obs at the annotated times)."""
    return next((o for o in obs if getattr(o, name) is not None), None)


def reading_pairs(track_obs: list[Obs], readings: list[Obs], fps: float) -> list[tuple[str, np.ndarray, np.ndarray, int]]:
    """[(field, pass-1 xy, reading xy, frame)] for every coordinate a reading gives on a frame where the
    pass-1 track has the same field: points, extent ends (matched in the closer order), box corners."""
    old = _frames(track_obs, fps)
    out = []
    for r in readings:
        f = frame_of(r.t, fps)
        for name in FIELDS:
            new, p = getattr(r, name), _first_with(old.get(f, []), name)
            if new is None or p is None:
                continue
            a, b = np.asarray(getattr(p, name), float).reshape(-1, 2), np.asarray(new, float).reshape(-1, 2)
            if name == "extent" and (np.linalg.norm(a - b[::-1], axis=1).max() < np.linalg.norm(a - b, axis=1).max()):
                b = b[::-1]
            out += [(name, a[i], b[i], f) for i in range(len(a))]
    return out


def reading_delta(track: Track, obs: list[Obs], fps: float) -> float | None:
    """Largest distance (px) between the readings and the pass-1 obs on the same frames (extent ends
    matched in the closer order, points, box corners unless the frame has extents on both sides);
    None when no frame is shared. Each field is compared with the frame's first pass-1 obs carrying it."""
    ext_frames = {f for n, _, _, f in reading_pairs(track.obs, obs, fps) if n == "extent"}
    ds = [float(np.linalg.norm(b - a)) if n != "box" else float(np.abs(b - a).max())
          for n, a, b, f in reading_pairs(track.obs, obs, fps) if not (n == "box" and f in ext_frames)]
    return round(max(ds), 2) if ds else None


def _median_xy(vs) -> np.ndarray:
    return np.median(np.asarray(vs, float).reshape(-1, 2), axis=0)


def _corrections(track_obs: list[Obs], readings: list[Obs], fps: float) -> dict:
    """The systematic change the readings make to the pass-1 obs of the same frames, per field:
    point -> median shift; extent -> median midpoint shift and length ratio (median of the readings'
    lengths / median of pass 1's); box -> median centre shift and width / height ratios."""
    old = _frames(track_obs, fps)
    got: dict[str, list] = {n: [] for n in FIELDS}
    for r in readings:
        for n in FIELDS:
            p = _first_with(old.get(frame_of(r.t, fps), []), n)
            if getattr(r, n) is not None and p is not None:
                got[n].append((np.asarray(getattr(p, n), float).reshape(-1, 2),
                               np.asarray(getattr(r, n), float).reshape(-1, 2)))
    out: dict = {}
    if got["point"]:
        out["point"] = _median_xy([b[0] - a[0] for a, b in got["point"]])
    for n in ("extent", "box"):
        pairs = got[n]
        if not pairs:
            continue
        shift = _median_xy([b.mean(axis=0) - a.mean(axis=0) for a, b in pairs])
        if n == "extent":
            la = np.median([np.linalg.norm(a[1] - a[0]) for a, _ in pairs])
            lb = np.median([np.linalg.norm(b[1] - b[0]) for _, b in pairs])
            ratio = np.array([lb / la] * 2) if la > 0 else np.ones(2)
        else:
            sa = np.median([np.abs(a[1] - a[0]) for a, _ in pairs], axis=0)
            sb = np.median([np.abs(b[1] - b[0]) for _, b in pairs], axis=0)
            ratio = np.where(sa > 0, sb / np.where(sa > 0, sa, 1), 1.0)
        out[n] = (shift, ratio if np.all(np.isfinite(ratio)) and np.all(ratio > 0) else np.ones(2))
    return out


def _corrected(o: Obs, corr: dict) -> Obs:
    """A pass-1 obs with the readings' systematic change applied (extents scaled along themselves about
    their shifted midpoint, boxes about their shifted centre)."""
    n = Obs(**asdict(o))
    if n.point is not None and "point" in corr:
        n.point = [float(v) for v in np.asarray(n.point, float) + corr["point"]]
    if n.extent is not None and "extent" in corr:
        shift, ratio = corr["extent"]
        e = np.asarray(n.extent, float)
        mid, half = e.mean(axis=0) + shift, (e[1] - e[0]) / 2 * ratio[0]
        n.extent = [[float(v) for v in mid - half], [float(v) for v in mid + half]]
    if n.box is not None and "box" in corr:
        shift, ratio = corr["box"]
        b = np.asarray(n.box, float).reshape(2, 2)
        c, half = b.mean(axis=0) + shift, (b[1] - b[0]) / 2 * ratio
        n.box = [float(v) for v in np.r_[c - half, c + half]]
    return n


def merge_readings(track_obs: list[Obs], readings: list[Obs], fps: float) -> list[Obs] | None:
    """The pass-1 track with the readings merged in: on a read frame, each field the reading gives
    replaces that field of the frame's first pass-1 obs having it (keeping pass 1's time); every other
    pass-1 coordinate gets the readings' systematic change (_corrections), so a track keeps all its
    frames (the geometry takes medians / local fits over them) and identical readings leave it
    unchanged. Readings of frames pass 1 has no obs on are added. None when no reading shares a frame
    with the pass-1 track (nothing to merge into)."""
    old = _frames(track_obs, fps)
    read = {frame_of(r.t, fps): r for r in readings}
    if not set(read) & set(old):
        return None
    corr = _corrections(track_obs, readings, fps)
    owner = {}                                 # (frame, field) -> the pass-1 obs taking the reading's value
    for f, r in read.items():
        for n in FIELDS:
            if f in old and getattr(r, n) is not None:
                owner[(f, n)] = _first_with(old[f], n) or old[f][0]
    out = []
    for o in track_obs:
        f = frame_of(o.t, fps)
        n = _corrected(o, corr)
        for name in FIELDS:
            if owner.get((f, name)) is o:
                setattr(n, name, copy.deepcopy(getattr(read[f], name)))
        out.append(n)
    out += [Obs(**asdict(r)) for f, r in read.items() if f not in old]
    return sorted(out, key=lambda o: o.t)


def _same_obs(a: list[Obs], b: list[Obs]) -> bool:
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if abs(x.t - y.t) > 1e-9:
            return False
        for n in FIELDS:
            u, v = getattr(x, n), getattr(y, n)
            if (u is None) != (v is None) or (u is not None and not np.allclose(
                    np.asarray(u, float), np.asarray(v, float), rtol=0, atol=1e-6)):
                return False
    return True


def pixel_space_suspect(pairs: list, evidence: list[dict]) -> bool:
    """True when the readings that moved (>= SPACE_MIN_PX from pass 1) are mostly pass 1's own positions
    expressed in an evidence image's pixels instead of original ones: u = margin + (x - x0) * zoom
    (with or without the tick-band margins) for an image of the same frame (a downscaled full frame
    read as if it were original, a crop read without its offset / zoom)."""
    maps = {}
    for e in evidence or []:
        x0, y0 = e["region"][:2]
        z = float(e["zoom"])
        for ml, mt in ((MARGIN_L, MARGIN_T), (0, 0)):
            if not (ml == 0 and x0 == 0 and y0 == 0 and z == 1):
                maps.setdefault(int(e["frame"]), []).append((np.array([ml, mt], float), np.array([x0, y0], float), z))
    moved = [(a, b, f) for _, a, b, f in pairs if np.linalg.norm(b - a) >= SPACE_MIN_PX]
    if not moved:
        return False
    hits = sum(any(np.linalg.norm(b - (m + (a - o) * z)) <= max(SPACE_TOL_PX, 0.25 * np.linalg.norm(b - a))
                   for m, o, z in maps.get(f, [])) for a, b, f in moved)
    return 2 * hits >= len(moved)


def apply_track_fixes(ctx: VideoContext, parsed: dict, shown: set[int], remeasure: bool = False,
                      evidence: list[dict] | None = None) -> tuple[dict[str, Track], dict[str, dict]]:
    """(corrected track table, {tid: {"action", "problem", "applied", "flags", "delta_px"}}).
    Which tracks change: those the model marks "replace" and, with `remeasure`, every track the
    geometry reads only sizes / distances from (not one with a motion use: a dense or flow-refined
    pass-1 track beats a few readings) by the model's readings.
    How: a track without a motion use keeps its pass-1 obs with the readings merged in (merge_readings:
    read frames take the readings, the other frames the same systematic change), so readings equal to
    pass 1 change nothing; a motion track marked "replace", or a track whose readings share no frame
    with it, becomes exactly the readings, when they are usable (extents / boxes for a size use, >= 2
    located frames for motion, a located obs for a distance; else flag verify_replace_unusable) and
    not all within NOOP_PX of pass 1 on its own frames (flag verify_replace_noop: the prompt asks for no
    moves below 1 px, and such a "replace" would only trade a dense track for its evidence frames).
    Readings that look like evidence-image pixels rather than original ones (pixel_space_suspect) are
    not applied (flag verify_pixel_space). `applied` is set only when the track actually changed.
    delta_px: largest distance between a reading and the pass-1 obs of the same frame (reading_delta),
    a diagnostic of how much the model moved things."""
    W, H = ctx.image_size
    tracks = {k: copy.deepcopy(t) for k, t in ctx.tracks.items()}
    info: dict[str, dict] = {}
    for fix in parsed.get("tracks") or []:
        if not isinstance(fix, dict):
            continue
        tid = str(fix.get("track", "")).strip()
        if tid not in tracks or tid in info:
            continue
        flags: list[str] = []
        action = fix.get("action") if fix.get("action") in ACTIONS else "keep"
        rec = {"action": action, "problem": str(fix.get("problem") or ""), "applied": False, "flags": flags}
        dn = fix.get("depth_name")
        if isinstance(dn, str) and dn.strip() and ctx.is_3d and dn.strip() != tracks[tid].depth_name:
            tracks[tid].depth_name = dn.strip()
            rec["applied"] = True
            rec["depth_name"] = dn.strip()
        obs = [ob for o in fix.get("obs") or [] if isinstance(o, dict)
               and (ob := parse_obs(o, ctx.fps, shown, W, H, flags))]
        by_frame: dict[int, Obs] = {}
        for o in obs:
            by_frame[frame_of(o.t, ctx.fps)] = o
        obs = sorted(by_frame.values(), key=lambda o: o.t)
        p1 = ctx.tracks[tid].obs
        rec["delta_px"] = reading_delta(ctx.tracks[tid], obs, ctx.fps)
        uses = {u["use"] for u in tracks[tid].uses}
        motion = "motion" in uses
        if action == "replace" or (remeasure and obs and uses & {"size", "distance"} and not motion):
            if not obs:
                flags.append("verify_replace_unusable")
                info[tid] = rec
                continue
            if pixel_space_suspect(reading_pairs(p1, obs, ctx.fps), evidence or []):
                flags.append("verify_pixel_space")
                info[tid] = rec
                continue
            pairs = reading_pairs(p1, obs, ctx.fps)
            if motion and pairs and max(float(np.linalg.norm(b - a)) for _, a, b, _ in pairs) <= NOOP_PX and \
                    {frame_of(o.t, ctx.fps) for o in obs} <= {f for *_, f in pairs}:
                flags.append("verify_replace_noop")      # readings = pass 1: keep the dense / refined track
                info[tid] = rec
                continue
            new = None if motion else merge_readings(p1, obs, ctx.fps)
            if new is None:
                located = [o for o in obs if o.point is not None or o.box is not None]
                ok = ("size" not in uses or any(o.extent or o.box for o in obs)) \
                    and (not motion or len({o.t for o in located}) >= 2) \
                    and ("distance" not in uses or located)
                if not ok:
                    flags.append("verify_replace_unusable")
                    info[tid] = rec
                    continue
                new = obs
                flags.append("verify_track_replaced")
            else:
                flags.append("verify_track_merged")
            if not _same_obs(new, p1):
                tracks[tid].obs, tracks[tid].refined = new, False
                rec["applied"] = True
        info[tid] = rec
    return tracks, info


def apply_spec_fix(spec: QuestionSpec, fix: dict | None, target_unit: str, flags: list[str]) -> QuestionSpec:
    """Spec with the listed fields changed. Values and units stay pass 1's (from the texts); a kind
    change must keep the dimension of the prior's value / the asked unit, else it is ignored."""
    spec = copy.deepcopy(spec)
    if not isinstance(fix, dict):
        return spec
    for who in ("target", "prior"):
        f = fix.get(who)
        if not isinstance(f, dict):
            continue
        q = getattr(spec, who)
        for name in [c for c in (f.get("change") or []) if c in SPEC_FIELDS]:
            v = f.get(name)
            if name == "kind":
                if v not in KINDS:
                    continue
                want = KIND_DIM.get(q.kind) if who == "prior" else (KIND_DIM.get(q.kind) if not target_unit else
                                                                    _unit_dim(target_unit) or KIND_DIM.get(q.kind))
                if KIND_DIM.get(v) != want:
                    flags.append(f"verify_{who}_kind_rejected")
                    continue
                q.kind = v
            elif name == "objects":
                if isinstance(v, list) and all(isinstance(x, str) for x in v) and v:
                    q.objects = [str(x) for x in v]
                else:
                    continue
            elif name == "dimension":
                q.dimension = str(v or "")
            elif name == "time":
                q.time = ca._num(v)
            elif name == "window":
                q.window = [float(min(v)), float(max(v))] if _xy(v) else None
            elif name == "axis":
                q.axis = v if v in ca.AXES else "any"
            flags.append(f"verify_{who}_{name}")
    return spec


def _unit_dim(unit: str) -> str | None:
    from .parse import _UNITS, canonical_unit
    cu = canonical_unit(unit)
    return _UNITS[cu][1] if cu in _UNITS else None


def recompute(meta: dict, parsed: dict | None, rule: str = DEFAULT_RULE,
              pass1_rule: str = combine.DEFAULT_RULE) -> list[dict]:
    """One row per question of a verify record: the corrected tracks and specs re-solved by
    qp.geometry and the answer picked by `rule` (module docstring). Columns: id, parsed_value,
    geo_value, direct_value, method, flags, geo_method, pass1_value, geo1_value, verdict,
    final_answer, verify_how."""
    if rule not in RULES:
        raise ValueError(f"unknown rule {rule!r} (expected one of {RULES})")
    ctx = context_from_meta(meta)
    shown = set(meta.get("frames_shown") or [])
    parsed = parsed or {}
    tracks, tinfo = apply_track_fixes(ctx, parsed, shown, remeasure=rule == "remeasure",
                                      evidence=meta.get("evidence"))
    changed = {tid for tid, r in tinfo.items() if r["applied"]}
    verdicts = {}
    for v in parsed.get("questions") or []:
        if isinstance(v, dict) and isinstance(v.get("qid"), int) and v["qid"] not in verdicts:
            verdicts[v["qid"]] = v
    rows = []
    for q in ctx.questions:
        geo1 = solve_question(q.spec, role_tracks(q, ctx.tracks), ctx.image_size, ctx.fps, ctx.video_source)
        p1, how1, flags1 = select(geo1, q.direct, q.ann_flags, q.spec, ctx.video_source, pass1_rule)
        v = verdicts.get(q.qid)
        flags: list[str] = []
        row = {"id": q.qid, "pass1_value": p1, "geo1_value": geo1.value if valid(geo1.value) else math.nan,
               "geo2_value": math.nan, "verdict": v.get("verdict") if v else "missing", "final_answer": math.nan,
               "verify_how": "pass1", "delta_px": max((d for _, t in q.roles
                                                      if (d := (tinfo.get(t) or {}).get("delta_px")) is not None),
                                                     default=math.nan)}
        if v is None:
            flags.append("verify_missing")
        fa = ca._num(v.get("final_answer")) if v else None
        row["final_answer"] = fa if valid(fa) else math.nan
        spec2 = apply_spec_fix(q.spec, v.get("spec_fix") if v else None, q.spec.target.unit, flags)
        touched = bool(changed & {tid for _, tid in q.roles}) or spec2 != q.spec
        geo2 = None
        if touched:
            q2 = QCtx(**{**q.__dict__, "spec": spec2})
            geo2 = solve_question(spec2, role_tracks(q2, tracks), ctx.image_size, ctx.fps, ctx.video_source)
            flags.append("verify_touched")
        verdict = row["verdict"]
        # pass-1 row (method = pass 1's selection) unless a branch below takes over
        value, method, branch, sel_flags = p1, how1, "pass1", flags1
        gv, dv, gm = geo1.value, q.direct, geo1.method
        direct = q.direct
        if rule == "verify_vdirect" and verdict in ("corrected", "accept_direct") and valid(fa):
            direct = fa
        if rule == "pass1":
            pass
        elif rule == "verify_final":
            if valid(fa):
                value, method, branch = fa, "verify_final", "final_answer"
        elif verdict == "accept_direct" and valid(direct):
            value, method, branch, gv, dv = float(direct), "direct", "accept_direct", math.nan, direct
        elif touched and geo2 is not None and valid(geo2.value):
            if valid(fa) and max(geo2.value / fa, fa / geo2.value) > VERIFY_AGREE:
                flags.append("verify_inconsistent")
            else:
                value, method, sel_flags = select(geo2, direct, q.ann_flags, spec2, ctx.video_source, pass1_rule)
                branch, gv, dv, gm = "recomputed", geo2.value, direct, geo2.method
        elif touched:
            flags.append("verify_geometry_failed")
        elif verdict == "corrected":
            flags.append("verify_no_change")
        if not valid(value):
            value, method, branch = p1, how1, "pass1"
        row.update({"parsed_value": value, "geo_value": gv if valid(gv) else math.nan,
                    "direct_value": dv if valid(dv) else math.nan, "method": method,
                    "flags": ";".join(sorted(set(list(sel_flags) + flags))), "geo_method": gm or "",
                    "verify_how": branch})
        if geo2 is not None:
            row["geo2_value"] = geo2.value if valid(geo2.value) else math.nan
        rows.append(row)
    return rows


COLUMNS = ["id", "parsed_value", "geo_value", "direct_value", "method", "flags", "geo_method", "pass1_value",
           "geo1_value", "geo2_value", "verdict", "final_answer", "verify_how", "delta_px"]
