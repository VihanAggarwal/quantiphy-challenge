"""Model-free post-processing of test predictions from the structure of the test inputs.

    from qp.postprocess import apply_rules
    new, log = apply_rules(pred, test_df)          # pred: Series of answers indexed by qid

Three default rules, ported from the Track A probes (research/PROBES.md, probes 4 and 5). They read only test
INPUTS: video ids' structure, frames, and the question / prior / depth_info text of every test question.
They never read answers (an `answer` column in `test_df` is dropped on entry) and work on any model's
predictions (Track A Claude runs, Track B open-weight runs).

twin    A clip "<id>_segmented" is a pixel-aligned re-render of "<id>" on a plain background. Its question
        takes the original clip's answer when the normalised question text, the prior text (exact, up to
        whitespace), depth_info, unit and category all match. The frames decide whether the twin really is
        the same view: when a rotated / flipped original fits the segmented frame much better than the
        original as is (simulation_0017 and _0019 are rotated 90 degrees), or the frames cannot be read,
        the pair is skipped.
render  Lab clips captured_XXXX plus XXXXs / XXXXx are one event with replaced backgrounds. A motion
        question (speed, acceleration, displacement, path length) on an s/x render takes the base render's
        answer when question, prior, depth_info and unit match (judging motion needs the background).
        `render_mask` restricts the rule to some rows (Track A replays it on direct-routed answers only).
facts   Stated-fact transfer (scene-graph "T" and sibling-prior "SIB" of the probes, from text, not from
        a model's parse). Clips are joined into scene families by twins and lab renders, >= 2 shared
        depth_info numbers with >= 3 decimals, identical prior statements (>= 3 significant digits),
        identical prior text of simulation clips that share >= 2 questions, and near-identical frames.
        A question asking the size / speed / acceleration of an object takes the value another clip of
        its family STATES as a prior for that object (same head noun, qp.geometry.name_score >= 0.6),
        converted to the asked unit:
          - sizes: same dimension, and the clips are the same base clip or both simulation renders
            (assets reused across simulation scenes; lab and internet clips only within one event, so
            no props or people are pooled across events);
          - motion: the stated value is untimed or stated at the asked time; a speed question's object
            has no acceleration stated or asked in its clip; families exclude look-alike (frames) and
            identical-prior-text (series) links, since near-identical views can show different motion
            (an identical >= 3-digit prior statement, size or motion, still links). Tier 1 = the same
            moving object (same clip, identical render, same scenario = identical motion prior in one
            family, identical timed depth entries); tier 2 = the rest of the family (which can reach a
            same-scenario clip's family); a question uses its best tier only;
        skipped when that tier states different values (conflicting facts) or, for a speed, when the
        value is more than `speed_guard` x off the current prediction (the footage contradicts the
        statement: the reviewers' guard for the footage-B person speed of 1.3 m/s).
        Per-clip scale correction and pooling are the extended rules below; not ported (Claude-specific or
        speculative): lab kind split, single-clip data fixes, label-noise emulation on Claude's tracks.

Extended rules (Track B, off by default; see the section "extended rules" and research/trackb_rules/):
motionfam  sim3d motion facts: speeds / accelerations a sibling camera of the same Blender scene states (size-family
           links), gated by constant speed, 2% agreement and radial consistency with every depth track.
freefall   a 3D-simulation acceleration at time t whose frames show a vertical fall from rest -> 9.8 m/s^2.
labfacts   lab prop sizes stated in another lab event (basketball 23.2 cm, tennis ball 6.7 cm, ...).
kscale     per-clip scale correction from the clip's stated-fact misses (K; D3 by default).
pool       per-object pooling across the scene family (P; D2 cross-camera pooling, render / twin pooling with
           scope='base'): trimmed log-mean of one vote per clip or base clip, with spread / own-vote guards.
labpool    lab prop sizes pooled across events (LAB).
PRESETS["trackb"] is the set used for the Track B open-weight answers.

Order: facts, motionfam, freefall, labfacts (stated values; protected from the later rules), kscale, pool,
labpool, render, twin, so an s/x render or a segmented twin copies its source's FINAL answer; a row that
received its own stated fact keeps it. Frame-based links are cached under runs/_postprocess_cache/ (keyed by
file size and mtime), so a re-run is fast.
"""

from __future__ import annotations

import itertools
import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from qp.geometry import _tok_eq, _tokens, name_score
from qp.parse import _UNITS, canonical_unit

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CACHE = ROOT / "runs" / "_postprocess_cache"
DEFAULT_RULES = ("twin", "render", "facts")
EXTENDED_RULES = ("motionfam", "freefall", "labfacts", "kscale", "pool", "labpool")
RULES = DEFAULT_RULES + EXTENDED_RULES
LOG_COLUMNS = ["qid", "rule", "old", "new", "source_qid", "source_clip", "reason", "applied"]

MOTION_KINDS = ("speed", "acceleration", "displacement", "path_length")
FACT_KINDS = ("size", "speed", "acceleration")
KIND_DIM = {"size": "L", "speed": "V", "acceleration": "A"}
SI_UNIT = {"L": "m", "V": "m/s", "A": "m/s^2"}

MIN_NAME = 0.6          # object-name similarity for a stated fact (qp.geometry.name_score)
SPEED_GUARD = 2.0       # a transferred speed this far off the clip's own answer is a conflict
DEPTH_DECIMALS = 3      # depth_info numbers with >= 3 decimals identify a scene
DEPTH_MIN_SHARED = 2    # ... when two clips share at least this many of them
PRIOR_SIG_DIGITS = 3    # identical prior statements link clips when the value has >= 3 significant digits
SERIES_MIN_SHARED_Q = 2  # identical prior text links simulation clips that also share >= 2 questions
FRAME_NCC = 0.90        # near-identical views: thumbnail correlation (64x64 grey, first/middle/last frame)
RENDER_NCC, RENDER_MAD = 0.99, 0.3   # same render (identical motion): every aligned thumbnail this close

TWIN_FRAMES = (0.0, 0.25, 0.5, 0.75, 1.0)   # relative frame positions compared for a twin pair
TWIN_SIDE = 1024                            # long side the twin frames are compared at
TWIN_MAD_RATIO, TWIN_EDGE_RATIO = 0.5, 1.5  # a transform beating identity on both by these = rotated view
CACHE_VERSION = 3


# ----------------------------------------------------------------------------- ids and text

_LAB_RENDER = re.compile(r"^(captured_\d+[ab]?)([sxX])$")


def twin_original(video_id: str) -> str | None:
    """'simulation_0010_segmented' -> 'simulation_0010' (None for any other clip)."""
    v = str(video_id)
    return v[: -len("_segmented")] if v.endswith("_segmented") else None


def lab_base(video_id: str) -> str | None:
    """'captured_0013s' / 'captured_0034bx' -> 'captured_0013' / 'captured_0034b' (None otherwise)."""
    m = _LAB_RENDER.match(str(video_id))
    return m.group(1) if m else None


def base_id(video_id: str) -> str:
    """The clip a twin / lab render was made from (itself for an original clip)."""
    return twin_original(video_id) or lab_base(video_id) or str(video_id)


def is_simulation(video_id: str) -> bool:
    return str(video_id).startswith("simulation_")


def norm_question(q: str) -> str:
    """Lower case, '1.0s' == '1s', only letters, digits and dots kept."""
    q = re.sub(r"(\d+)\.0+(?!\d)", r"\1", str(q).lower())
    return re.sub(r"[^a-z0-9.]", "", q)


def norm_ws(s) -> str:
    return re.sub(r"\s+", " ", "" if s is None or (isinstance(s, float) and math.isnan(s)) else str(s)).strip()


def exact_text(s) -> str:
    """Text compared exactly except for whitespace ('= 90 cm' == '= 90cm'), for prior / depth_info keys."""
    return re.sub(r"\s+", "", norm_ws(s))


def _finite_pos(x) -> bool:
    try:
        x = float(x)
    except (TypeError, ValueError):
        return False
    return math.isfinite(x) and x > 0


# ----------------------------------------------------------------------------- inputs

def _questions(test_df: pd.DataFrame, video_root=None) -> pd.DataFrame:
    """Copy of the question table without answers, with the columns the rules use."""
    df = test_df.drop(columns=[c for c in ("answer", "ground_truth_posterior") if c in test_df.columns]).copy()
    if "ground_truth_prior" in df.columns and "prior" not in df.columns:
        df = df.rename(columns={"ground_truth_prior": "prior"})
    df["qid"] = df["qid"].astype(int)
    for col in ("prior", "depth_info", "question", "video_source", "category", "video_type", "inference_type"):
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str)
    if (df["category"] == "").any() and {"inference_type", "video_type"} <= set(df.columns):
        fill = [f"{i[:1]}{v[1:2]}" for i, v in zip(df.inference_type, df.video_type)]
        df["category"] = [c or f for c, f in zip(df.category, fill)]
    if "target_unit" not in df.columns:
        from qp.data import target_unit
        df["target_unit"] = df["question"].map(target_unit)
    df["target_unit"] = df["target_unit"].fillna("").astype(str)
    if video_root is not None:
        index = {p.stem.strip(): str(p) for p in Path(video_root).rglob("*.mp4")}
        df["video_path"] = df["video_id"].map(lambda v: index.get(str(v).strip(), ""))
    elif "video_path" not in df.columns:
        df["video_path"] = ""
    df["video_path"] = df["video_path"].fillna("").astype(str)
    return df.reset_index(drop=True)


def _row_unit(row, kind: str) -> str | None:
    """Canonical unit of the asked value (the kind's SI unit when the question names none); None when
    the unit's dimension does not fit the kind."""
    u = canonical_unit(str(row.target_unit or "")) if row.target_unit else None
    if u is None:
        return SI_UNIT[KIND_DIM[kind]]
    return u if u in _UNITS and _UNITS[u][1] == KIND_DIM[kind] else None


# ----------------------------------------------------------------------------- frames

def read_frames(path: str, positions=TWIN_FRAMES, side: int | None = None) -> tuple[list[np.ndarray | None], int]:
    """BGR frames at relative positions (0 = first, 1 = last) and the frame count. The list stays
    aligned with `positions` (None where that frame cannot be read, so two clips' frames are always
    paired by position); [] if the video or every frame is unreadable."""
    import cv2

    cap = cv2.VideoCapture(str(path))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    out: list[np.ndarray | None] = []
    if not cap.isOpened() or n <= 0:
        cap.release()
        return [], 0
    for p in positions:
        idx = int(round(float(p) * (n - 1)))
        frame = None
        for k in (idx, idx - 1, idx - 2):      # the container frame count can overshoot by a frame or two
            if k < 0:
                break
            cap.set(cv2.CAP_PROP_POS_FRAMES, k)
            ok, im = cap.read()
            if ok and im is not None:
                frame = im
                break
        if frame is not None and side:
            frame = _resize_max(frame, side)
        out.append(frame)
    cap.release()
    return (out if any(f is not None for f in out) else []), n


def _resize_max(img: np.ndarray, side: int) -> np.ndarray:
    import cv2

    h, w = img.shape[:2]
    s = side / max(h, w)
    if s >= 1:
        return img
    return cv2.resize(img, (max(1, round(w * s)), max(1, round(h * s))), interpolation=cv2.INTER_AREA)


def _foreground(seg: np.ndarray, min_px: int = 40, max_frac: float = 0.6) -> np.ndarray | None:
    """Mask of the kept object in a segmented frame: pixels far from the plain background colour (the
    frame's most common colour; a segmented frame is mostly background). None when there is too little
    or too much foreground to compare."""
    import cv2

    img = seg.astype(np.int16)
    q = img[::4, ::4].reshape(-1, 3) // 32
    code = q[:, 0] * 64 + q[:, 1] * 8 + q[:, 2]
    codes, counts = np.unique(code, return_counts=True)
    bg = np.median(img[::4, ::4].reshape(-1, 3)[code == codes[np.argmax(counts)]], axis=0)
    mask = (np.abs(img - bg).max(axis=2) > 40).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    if mask.sum() < min_px or mask.mean() > max_frac:
        return None
    return mask.astype(bool)


def _gradient(gray: np.ndarray) -> np.ndarray:
    import cv2

    g = cv2.GaussianBlur(gray.astype(np.float32), (3, 3), 0)
    return np.hypot(cv2.Sobel(g, cv2.CV_32F, 1, 0), cv2.Sobel(g, cv2.CV_32F, 0, 1))


_TRANSFORMS = {
    "identity": lambda x: x, "rot90": lambda x: np.rot90(x, 1), "rot180": lambda x: np.rot90(x, 2),
    "rot270": lambda x: np.rot90(x, 3), "flip_lr": lambda x: x[:, ::-1], "flip_ud": lambda x: x[::-1],
    "transpose": lambda x: np.transpose(x, (1, 0, 2)), "anti_transpose": lambda x: np.rot90(x, 2).transpose(1, 0, 2),
}


def twin_alignment(orig_frames: list[np.ndarray], seg_frames: list[np.ndarray], side: int = TWIN_SIDE) -> dict:
    """Is the segmented clip the same view as the original? Frames are paired by position. For every
    rotation / flip of the original (resized to the segmented frame when the aspect ratio fits) two
    scores are measured on the segmented frame's foreground: the colour difference (low = same pixels)
    and the original's edge strength along the foreground outline relative to its mean (high = the
    outline sits on the original's object edges; robust to a re-render's different shading).
    status: "rotated" when another transform beats the identity on both by a wide margin, "aligned"
    otherwise, "unknown" when no frame had a usable foreground."""
    import cv2

    per: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for a, b in zip(orig_frames, seg_frames):
        if a is None or b is None:
            continue
        bs = _resize_max(b, side)
        mask = _foreground(bs)
        if mask is None:
            continue
        m8 = mask.astype(np.uint8)
        outline = (m8 - cv2.erode(m8, np.ones((3, 3), np.uint8))).astype(bool)
        if outline.sum() < 20:
            continue
        hb, wb = bs.shape[:2]
        for name, tf in _TRANSFORMS.items():
            x = np.ascontiguousarray(tf(a))
            if abs((x.shape[1] / x.shape[0]) / (wb / hb) - 1) > 0.03:
                continue
            xs = cv2.resize(x, (wb, hb), interpolation=cv2.INTER_AREA)
            mad = float(np.abs(xs.astype(np.int16) - bs.astype(np.int16)).mean(axis=2)[mask].mean())
            grad = _gradient(cv2.cvtColor(xs, cv2.COLOR_BGR2GRAY))
            edge = float(grad[outline].mean() / (grad.mean() + 1e-6))
            per[name].append((mad, edge))
    if not per:
        return {"status": "unknown", "scores": {}}
    scores = {k: (float(np.mean([m for m, _ in v])), float(np.mean([e for _, e in v]))) for k, v in per.items()}
    if "identity" in scores:
        mi, ei = scores["identity"]
        better = [k for k, (m, e) in scores.items()
                  if k != "identity" and m < TWIN_MAD_RATIO * mi and e > TWIN_EDGE_RATIO * ei]
        status = "rotated" if better else "aligned"
        best = min(better, key=lambda k: scores[k][0]) if better else "identity"
    else:   # aspect ratio only fits a rotated original
        best = max(scores, key=lambda k: scores[k][1])
        status = "rotated"
    return {"status": status, "transform": best, "scores": {k: [round(m, 2), round(e, 3)] for k, (m, e) in scores.items()}}


def thumbnails(frames: list[np.ndarray]) -> np.ndarray:
    """64x64 grey thumbnails (uint8) of a clip's first / middle / last frames."""
    import cv2

    return np.stack([cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (64, 64), interpolation=cv2.INTER_AREA)
                     for f in frames]).astype(np.uint8)


def _unit_rows(th: np.ndarray) -> np.ndarray:
    x = th.reshape(len(th), -1).astype(np.float32)
    x = x - x.mean(axis=1, keepdims=True)
    n = np.linalg.norm(x, axis=1, keepdims=True)
    return x / np.where(n > 0, n, 1)


def frame_similarity(th_a: np.ndarray, th_b: np.ndarray) -> dict:
    """ncc: best correlation over all frame pairs (same scene, any moment); aligned_ncc / aligned_mad:
    worst correlation and largest mean abs difference over same-position frames (identical render)."""
    A, B = _unit_rows(th_a), _unit_rows(th_b)
    k = min(len(th_a), len(th_b))
    return {"ncc": float((A @ B.T).max()),
            "aligned_ncc": float(min(A[i] @ B[i] for i in range(k))),
            "aligned_mad": float(max(np.abs(th_a[i].astype(np.float32) - th_b[i].astype(np.float32)).mean()
                                     for i in range(k)))}


def frame_pairs(th: dict[str, dict], min_ncc: float = FRAME_NCC):
    """(a, b, frame_similarity) for clips of different base clips with the same aspect ratio whose
    thumbnails correlate >= min_ncc. th: {video_id: {"th": (3, 64, 64) uint8, "ar": float}}."""
    vs = sorted(th)
    if len(vs) < 2:
        return []
    U = np.stack([_unit_rows(th[v]["th"]) for v in vs])            # (N, 3, 4096)
    N, k = U.shape[:2]
    G = (U.reshape(N * k, -1) @ U.reshape(N * k, -1).T).reshape(N, k, N, k).max(axis=(1, 3))
    ar = np.array([th[v]["ar"] for v in vs])
    out = []
    for i, j in zip(*np.nonzero(np.triu(G >= min_ncc, 1))):
        a, b = vs[i], vs[j]
        if base_id(a) == base_id(b) or abs(ar[i] / ar[j] - 1) > 0.01:
            continue
        out.append((a, b, frame_similarity(th[a]["th"], th[b]["th"])))
    return out


class FrameCache:
    """Thumbnails and twin-alignment verdicts, stored under `cache_dir` (thumbs_v1.npz, twins_v1.json) and
    keyed by each video file's size and mtime (a changed file is re-read)."""

    def __init__(self, cache_dir=DEFAULT_CACHE):
        self.dir = Path(cache_dir) if cache_dir else None
        self._thumbs: dict[str, dict] = {}
        self._twins: dict[str, dict] = {}
        self._falls: dict[str, dict] = {}
        self._dirty = False
        if not self.dir:
            return
        try:
            self._falls.update(json.loads((self.dir / f"falls_v{CACHE_VERSION}.json").read_text()))
        except (OSError, ValueError):
            pass
        try:
            self._twins.update(json.loads((self.dir / f"twins_v{CACHE_VERSION}.json").read_text()))
        except (OSError, ValueError):
            pass
        try:
            with np.load(self.dir / f"thumbs_v{CACHE_VERSION}.npz", allow_pickle=False) as z:
                for v, k, n, ar, th in zip(z["ids"], z["keys"], z["n"], z["ar"], z["th"]):
                    self._thumbs[str(v)] = {"key": str(k), "n": int(n), "ar": float(ar), "th": th}
        except (OSError, ValueError, KeyError):
            pass

    @staticmethod
    def _key(path: str) -> str | None:
        if not path:
            return None
        try:
            st = Path(path).stat()
        except (OSError, TypeError):
            return None
        return f"{st.st_size}:{int(st.st_mtime)}"

    def thumbs(self, video_id: str, path: str) -> dict | None:
        """{"th": uint8 (3, 64, 64), "n": frames, "ar": width / height} or None (no readable video)."""
        key = self._key(path)
        if key is None:
            return None
        c = self._thumbs.get(video_id)
        if c is None or c.get("key") != key:
            frames, n = read_frames(path, (0.0, 0.5, 1.0))
            if len(frames) != 3 or any(f is None for f in frames):
                return None
            h, w = frames[0].shape[:2]
            c = {"key": key, "n": n, "ar": w / h, "th": thumbnails(frames)}
            self._thumbs[video_id] = c
            self._dirty = True
        return c

    def twin(self, orig: str, orig_path: str, seg: str, seg_path: str) -> dict:
        ka, kb = self._key(orig_path), self._key(seg_path)
        if ka is None or kb is None:
            return {"status": "missing"}
        name, key = f"{orig}|{seg}", f"{ka}|{kb}"
        c = self._twins.get(name)
        if c is None or c.get("key") != key:
            fa, _ = read_frames(orig_path, TWIN_FRAMES, side=TWIN_SIDE)
            fb, _ = read_frames(seg_path, TWIN_FRAMES, side=TWIN_SIDE)
            c = dict(twin_alignment(fa, fb) if fa and fb else {"status": "unknown", "scores": {}}, key=key)
            self._twins[name] = c
            self._dirty = True
        return c

    def free_fall(self, video_id: str, path: str, t: float, fps: float) -> bool:
        key = self._key(path)
        if key is None:
            return False
        name = f"{video_id}|{t:g}|{fps:g}"
        c = self._falls.get(name)
        if c is None or c.get("key") != key:
            c = {"key": key, "fall": free_fall(path, t, fps)}
            self._falls[name] = c
            self._dirty = True
        return bool(c["fall"])

    def save(self) -> None:
        if not (self.dir and self._dirty):
            return
        self.dir.mkdir(parents=True, exist_ok=True)
        p = self.dir / f"falls_v{CACHE_VERSION}.json"
        p.with_suffix(".tmp").write_text(json.dumps(self._falls, indent=0))
        p.with_suffix(".tmp").replace(p)
        p = self.dir / f"twins_v{CACHE_VERSION}.json"
        p.with_suffix(".tmp").write_text(json.dumps(self._twins, indent=0))
        p.with_suffix(".tmp").replace(p)
        ids = sorted(self._thumbs)
        p = self.dir / f"thumbs_v{CACHE_VERSION}.npz"
        tmp = self.dir / f"thumbs_v{CACHE_VERSION}.tmp.npz"
        np.savez_compressed(tmp, ids=np.array(ids, dtype=str),
                            keys=np.array([self._thumbs[v]["key"] for v in ids], dtype=str),
                            n=np.array([self._thumbs[v]["n"] for v in ids], dtype=np.int64),
                            ar=np.array([self._thumbs[v]["ar"] for v in ids], dtype=np.float64),
                            th=np.stack([self._thumbs[v]["th"] for v in ids]) if ids else np.zeros((0, 3, 64, 64), np.uint8))
        tmp.replace(p)
        self._dirty = False


# ----------------------------------------------------------------------------- rule: twin / render

def _copy_rule(cur: pd.Series, df: pd.DataFrame, rule: str, rows: pd.DataFrame, source_of, keyf,
               protected: set[int], log: list, eligible=None, reason="") -> None:
    """Rows take the current answer of their unique source row (same key in the source clip)."""
    by_key = defaultdict(list)
    for r in df.itertuples():
        by_key[(r.video_id, keyf(r))].append(int(r.qid))
    for r in rows.itertuples():
        q = int(r.qid)
        if q not in cur.index or (eligible is not None and not eligible(q)):
            continue
        src_clip = source_of(r.video_id)
        srcs = [s for s in by_key.get((src_clip, keyf(r)), []) if s in cur.index and _finite_pos(cur[s])]
        if not srcs:
            continue
        vals = {round(float(cur[s]), 12) for s in srcs}
        old = float(cur[q])
        if len(vals) != 1:
            log.append(dict(qid=q, rule=rule, old=old, new=math.nan, source_qid=srcs[0], source_clip=src_clip,
                            reason=f"skipped: {len(srcs)} source rows disagree", applied=False))
            continue
        if q in protected:
            log.append(dict(qid=q, rule=rule, old=old, new=float(cur[srcs[0]]), source_qid=srcs[0],
                            source_clip=src_clip, reason="skipped: row has its own stated fact", applied=False))
            continue
        new = float(cur[srcs[0]])
        cur[q] = new
        log.append(dict(qid=q, rule=rule, old=old, new=new, source_qid=srcs[0], source_clip=src_clip,
                        reason=reason, applied=True))


def _twin_rule(cur, df, frames: FrameCache | None, protected, log) -> None:
    clips = set(df.video_id)
    paths = dict(zip(df.video_id, df.video_path))
    seg = df[df.video_id.map(lambda v: twin_original(v) in clips)]
    status = {}
    for v in sorted(set(seg.video_id)):
        o = twin_original(v)
        st = frames.twin(o, paths.get(o, ""), v, paths.get(v, "")) if frames else {"status": "missing"}
        status[v] = st
    ok = {v for v, s in status.items() if s["status"] == "aligned"}
    for v, s in sorted(status.items()):
        if s["status"] != "aligned":
            for r in seg[(seg.video_id == v) & seg.qid.isin(cur.index)].itertuples():
                log.append(dict(qid=int(r.qid), rule="twin", old=float(cur[int(r.qid)]), new=math.nan,
                                source_qid=math.nan, source_clip=twin_original(v), applied=False,
                                reason=f"skipped: twin frames {s['status']}" +
                                       (f" ({s.get('transform')} fits the original)" if s["status"] == "rotated" else "")))

    def key(r):
        return (norm_question(r.question), exact_text(r.prior), exact_text(r.depth_info), r.target_unit, r.category)

    _copy_rule(cur, df, "twin", seg[seg.video_id.isin(ok)], twin_original, key, protected, log,
               reason="segmented twin takes the original clip's answer (same question, prior, depth_info)")


def _render_rule(cur, df, protected, log, eligible=None) -> None:
    from qp.open.qwen_vl import parse_question_text

    clips = set(df.video_id)
    rend = df[df.video_id.map(lambda v: lab_base(v) in clips)]
    rend = rend[[parse_question_text(q)["kind"] in MOTION_KINDS for q in rend.question]]

    def key(r):
        return (norm_question(r.question), exact_text(r.prior), exact_text(r.depth_info), r.target_unit, r.category)

    _copy_rule(cur, df, "render", rend, lab_base, key, protected, log, eligible=eligible,
               reason="lab s/x render takes the base render's motion answer (same question, prior, depth_info)")


# ----------------------------------------------------------------------------- rule: facts

_CUT_OBJECT = re.compile(r"\s+(?:from|during|throughout|over|between|at|when|before|after|until)\b.*$", re.I)
_TIMED_LINE = re.compile(r"\bat\s+(?:time\s+)?(?:t\s*=\s*)?[\d.]+\s*s\b|\bfrom\s+(?:t\s*=\s*)?[\d.]+|\bbefore\b|"
                         r"\bafter\b|^\s*t\s*=", re.I)
_GRAVITY = re.compile(r"gravit|free.?fall|=\s*9\.[78]\d*\s*m\s*/\s*s", re.I)
_ACCEL_WORD = re.compile(r"\baccel", re.I)
_DIM_SYN = {"body length": "length", "tall": "height", "long": "length", "wide": "width", "caliber": "calibre"}


def _clean_object(name: str) -> str:
    return _CUT_OBJECT.sub("", re.sub(r"^(?:the|a|an)\s+", "", str(name).strip(), flags=re.I)).strip()


def _head(name: str) -> str:
    """Head noun: last token before a preposition ('tire of the yellow car' -> 'tire')."""
    core = re.split(r"\s+(?:of|in|on|with|near|wearing)\s+", str(name).strip(), maxsplit=1, flags=re.I)[0]
    toks = _tokens(core)
    return toks[-1] if toks else ""


def _same_object(a: str, b: str) -> float:
    """name_score, 0 unless the head nouns agree ('yellow car' never matches 'tire of the yellow car')."""
    ha, hb = _head(a), _head(b)
    if not ha or not hb or not _tok_eq(ha, hb):
        return 0.0
    return name_score(a, b)


@dataclass(frozen=True)
class Fact:
    video_id: str
    line: str
    kind: str
    obj: str
    dimension: str
    si: float
    time: float | None
    timed: bool


def _parse_facts(df: pd.DataFrame) -> list[Fact]:
    from qp.open.qwen_vl import parse_prior_text

    out = []
    for (v, prior), _ in df.groupby(["video_id", "prior"], sort=True):
        for line in str(prior).split("\n"):
            if not line.strip() or _GRAVITY.search(line):
                continue
            p = parse_prior_text(line)
            if p["kind"] == "speed" and _ACCEL_WORD.search(line) and not re.search(r"speed|velocit", line, re.I):
                p["kind"] = "acceleration"     # "acceleration of the trolley = 1.507m/s": a unit typo
            if p["kind"] not in FACT_KINDS or p["gravity"] or p.get("ambiguous") or not p["objects"]:
                continue
            if not _finite_pos(p["value_si"]):
                continue
            obj = _clean_object(p["objects"][0])
            if not obj:
                continue
            dim = _DIM_SYN.get(p["dimension"], p["dimension"]) if p["kind"] == "size" else ""
            out.append(Fact(v, line.strip(), p["kind"], obj, dim, float(p["value_si"]), p["time"],
                            p["time"] is not None or bool(_TIMED_LINE.search(line))))
    return list(dict.fromkeys(out))


def _sig_digits(x: float) -> int:
    return len(f"{abs(x):g}".replace(".", "").replace("-", "").lstrip("0").split("e")[0])


def _depth_numbers(text: str) -> set[str]:
    return set(re.findall(r"=\s*([0-9]+\.[0-9]{%d,})" % DEPTH_DECIMALS, str(text)))


def _depth_entries(text: str) -> dict[str, tuple]:
    """{object name: sorted ((time or None, distance), ...)} from depth_info text."""
    out = defaultdict(list)
    for line in str(text).split("\n"):
        m = re.search(r"(?:t\s*=\s*([\d.]+)\s*s?\s*,\s*)?distance_(.+?)_camera\s*=\s*([\d.]+)", line)
        if m:
            t, obj, d = m.groups()
            out[obj.replace("_", " ").lower()].append((float(t) if t else None, float(d)))
    return {k: tuple(sorted(v, key=lambda e: (e[0] is None, e[0] or 0.0))) for k, v in out.items()}


class _UF:
    def __init__(self):
        self.p: dict = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        self.p[self.find(a)] = self.find(b)


def scene_links(df: pd.DataFrame, facts: list[Fact], frames: FrameCache | None = None) -> dict[str, list]:
    """Links between base clips (twins and lab renders are already one base), by kind:
    depth     share >= DEPTH_MIN_SHARED depth_info numbers with >= 3 decimals
    prior     state the same quantity of the same object with the same value (>= 3 significant digits)
    series    simulation clips with identical non-gravity prior text that also ask >= 2 identical questions
    frames    near-identical views (thumbnail correlation >= FRAME_NCC; not segmented, not lab)
    render    identical renders (every same-position thumbnail nearly equal: identical motion)
    scenario  simulation clips of one family (all links above) stating the identical non-gravity MOTION
              prior (the same simulated event)."""
    links: dict[str, list] = {k: [] for k in ("depth", "prior", "series", "frames", "render", "scenario")}
    df = df.assign(base=df.video_id.map(base_id))
    nums = defaultdict(set)
    for b, di in zip(df.base, df.depth_info):
        nums[b] |= _depth_numbers(di)
    for a, b in itertools.combinations(sorted(b for b in nums if nums[b]), 2):
        if len(nums[a] & nums[b]) >= DEPTH_MIN_SHARED:
            links["depth"].append((a, b))
    stated = defaultdict(set)
    for f in facts:
        if _sig_digits(f.si) >= PRIOR_SIG_DIGITS:
            stated[(f.kind, " ".join(_tokens(f.obj)), f.dimension, round(f.si, 9), f.time)].add(base_id(f.video_id))
    for bs in stated.values():
        bs = sorted(bs)
        links["prior"] += [(bs[0], b) for b in bs[1:]]
    qsets = df.groupby("base").question.agg(lambda s: set(map(norm_question, s))).to_dict()
    sim = df[df.video_id.map(is_simulation) & ~df.prior.str.contains(_GRAVITY)]
    sim = sim.assign(pn=sim.prior.map(lambda p: re.sub(r"\s+", "", p.lower())))
    for _, g in sim.groupby("pn"):
        bs = sorted(set(g.base))
        for a, b in itertools.combinations(bs, 2):
            if len(qsets[a] & qsets[b]) >= SERIES_MIN_SHARED_Q:
                links["series"].append((a, b))
    if frames is not None:
        clips = sorted(v for v in set(df.video_id) if not twin_original(v) and not str(v).startswith("captured_"))
        paths = dict(zip(df.video_id, df.video_path))
        th = {v: t for v in clips if (t := frames.thumbs(v, paths.get(v, ""))) is not None}
        for a, b, s in frame_pairs(th):
            links["frames"].append((a, b))
            if th[a]["n"] == th[b]["n"] and s["aligned_ncc"] >= RENDER_NCC and s["aligned_mad"] <= RENDER_MAD:
                links["render"].append((a, b))
    fam = scene_families(df, links)
    moving = sim[sim.prior.str.contains(r"speed|velocit|accel", case=False)]
    for _, g in moving.groupby([moving.pn, moving.video_id.map(fam)]):
        bs = sorted(set(g.base))
        links["scenario"] += [(bs[0], b) for b in bs[1:]]
    return links


SIZE_LINKS = ("depth", "prior", "series", "frames", "render", "scenario")
MOTION_LINKS = ("depth", "prior", "render", "scenario")     # not by look (frames) or identical prior text (series)


def scene_families(df: pd.DataFrame, links: dict[str, list], kinds=SIZE_LINKS) -> dict[str, str]:
    """video_id -> family id (union of the base clips joined by links of the given kinds)."""
    uf = _UF()
    for v in df.video_id:
        uf.find(base_id(v))
    for k in kinds:
        for a, b in links.get(k, []):
            uf.union(base_id(a), base_id(b))
    return {v: uf.find(base_id(v)) for v in df.video_id}


def _accel_objects(df: pd.DataFrame, facts: list[Fact]) -> dict[str, list[str]]:
    """Objects whose acceleration a clip states or asks (their speed is not constant)."""
    from qp.open.qwen_vl import parse_question_text

    out = defaultdict(list)
    for f in facts:
        if f.kind == "acceleration":
            out[f.video_id].append(f.obj)
    for v, q in zip(df.video_id, df.question):
        t = parse_question_text(q)
        if t["kind"] == "acceleration" and t["objects"]:
            out[v].append(_clean_object(t["objects"][0]))
    return out


def _depth_identical(da: dict, db: dict, oa: str, ob: str) -> bool:
    """Both clips list the same timed distances (>= 2 entries) for the object: the same motion."""
    for ka, ea in da.items():
        if name_score(ka, oa) < 0.5 or len(ea) < 2:
            continue
        for kb, eb in db.items():
            if name_score(kb, ob) >= 0.5 and ea == eb:
                return True
    return False


CANDIDATE_COLUMNS = ["qid", "video_id", "kind", "obj", "source_clip", "line", "si", "value", "unit", "name_score",
                     "link", "tier"]


def stated_facts(df: pd.DataFrame, frames: FrameCache | None = None) -> pd.DataFrame:
    """Every (question, stated fact) pair the facts rule considers: qid, value (in the question's unit),
    source clip / line, link and tier. Sizes: one tier (the scene family). Motion: tier 1 = the same
    moving object (same clip, identical render, same scenario, identical depth track), tier 2 = the
    wider family by text / depth links; a question uses its best tier only. Differing values in that
    tier = conflict."""
    from qp.open.qwen_vl import parse_question_text

    df = _questions(df)
    facts = _parse_facts(df)
    links = scene_links(df, facts, frames)
    fam_size = scene_families(df, links, SIZE_LINKS)
    fam_motion = scene_families(df, links, MOTION_LINKS)
    scen = scene_families(df, links, ("render", "scenario"))
    accel = _accel_objects(df, facts)
    by_fam = defaultdict(list)
    for f in facts:
        by_fam[(fam_size[f.video_id], "size")].append(f)
        by_fam[(fam_motion[f.video_id], "motion")].append(f)
    depth = {v: _depth_entries(di) for v, di in zip(df.video_id, df.depth_info)}
    rows = []
    for r in df.itertuples():
        t = parse_question_text(r.question)
        if t["kind"] not in FACT_KINDS or len(t["objects"]) != 1:
            continue
        obj = _clean_object(t["objects"][0])
        unit = _row_unit(r, t["kind"])
        if not obj or unit is None:
            continue
        dim = _DIM_SYN.get(t["dimension"], t["dimension"])
        own = {norm_ws(x) for x in str(r.prior).split("\n")}
        motion = t["kind"] != "size"
        if motion and t["kind"] == "speed" and any(_same_object(obj, a) >= MIN_NAME for a in accel.get(r.video_id, [])):
            continue
        fam = fam_motion[r.video_id] if motion else fam_size[r.video_id]
        for f in by_fam[(fam, "motion" if motion else "size")]:
            if f.kind != t["kind"]:
                continue
            if f.video_id == r.video_id and norm_ws(f.line) in own:
                continue                                   # the question's own prior
            ns = _same_object(obj, f.obj)
            if ns < MIN_NAME:
                continue
            same_base = base_id(f.video_id) == base_id(r.video_id)
            if not (same_base or (is_simulation(f.video_id) and is_simulation(r.video_id))):
                continue
            tier = 1
            if not motion:
                if dim != f.dimension:
                    continue
                link = "same clip" if same_base else "simulation family"
            else:
                if f.timed:
                    tq = t["time"]
                    if t["window"] is not None or tq is None or f.time is None or abs(tq - f.time) > 1e-6:
                        continue
                if same_base:
                    link = "same clip"
                elif scen[f.video_id] == scen[r.video_id]:
                    link = "same scenario"
                elif _depth_identical(depth[r.video_id], depth[f.video_id], obj, f.obj):
                    link = "identical depth track"
                else:
                    link, tier = "scene family", 2
            rows.append(dict(qid=int(r.qid), video_id=r.video_id, kind=t["kind"], obj=obj, source_clip=f.video_id,
                             line=f.line, si=f.si, value=f.si / _UNITS[unit][0], unit=unit, name_score=round(ns, 3),
                             link=link, tier=tier))
    return pd.DataFrame(rows, columns=CANDIDATE_COLUMNS)


def _facts_rule(cur, df, frames, log, speed_guard=SPEED_GUARD) -> set[int]:
    cand = stated_facts(df, frames)
    applied = set()
    for q, g in cand[cand.qid.isin(cur.index)].groupby("qid", sort=True):
        g = g[g.tier == g.tier.min()]
        old = float(cur[q])
        vals = np.unique(np.round(g.value.to_numpy(float), 9))
        src = ",".join(sorted(set(g.source_clip)))
        lines = "; ".join(sorted(set(g.line)))
        if len(vals) != 1:
            log.append(dict(qid=q, rule="facts", old=old, new=math.nan, source_qid=math.nan, source_clip=src,
                            applied=False, reason=f"skipped: the family states conflicting values ({lines})"))
            continue
        new = float(vals[0])
        if g.kind.iloc[0] == "speed" and speed_guard and _finite_pos(old) and max(new / old, old / new) > speed_guard:
            log.append(dict(qid=q, rule="facts", old=old, new=new, source_qid=math.nan, source_clip=src, applied=False,
                            reason=f"skipped: stated speed '{lines}' is >{speed_guard:g}x off the clip's own answer "
                                   f"(footage contradicts the family statement)"))
            continue
        cur[q] = new
        applied.add(q)
        log.append(dict(qid=q, rule="facts", old=old, new=new, source_qid=math.nan, source_clip=src, applied=True,
                        reason=f"stated by {src}: '{lines}' ({', '.join(sorted(set(g.link)))})"))
    return applied


# ----------------------------------------------------------------------------- extended rules (Track B)
#
# Scene-family rules ported from the Track A probes 5-8 and the 2026-10-12 studies (research/PROBES.md), rebuilt
# on test inputs only (question / prior / depth_info text, frames) and the answers being post-processed. Every
# rule is switchable; none is in DEFAULT_RULES. Claude-specific parts of the Track A versions (Claude's tracks,
# clicks, hand-checked identity tables, eye-verified scene groups, label-noise emulation on Claude's 3D tracks)
# are not ported.

DIM_OF_KIND = {"size": "L", "distance": "L", "displacement": "L", "path_length": "L", "camera_distance": "L",
               "speed": "V", "acceleration": "A"}
POOL_KINDS = ("size", "speed", "acceleration", "displacement", "path_length", "distance")
POOL_TAU, POOL_CAP2, POOL_SMAX = 0.15, 0.3, 0.5
LAB_NAME = 0.8           # lab props: object names this close are one prop (Track A lab pooling)
LAB_SPREAD2, LAB_DEV = 2.0, 1.6
MF_AGREE, MF_RADIAL = 0.02, 1.05
K_KINDS = ("size", "speed")
G_EARTH = 9.8

# Track B (open-weight answers, research/trackb_rules): stated values of the family (facts, motionfam,
# freefall, labfacts) without the 2x "footage contradicts" guard (open-model misses, not the footage, explain a 2x
# disagreement), plus cross-clip pooling with base-clip votes and a 1.6x own-vote guard. Twin / render copies,
# K and lab pooling are left out (validation and stated-fact checks neutral or negative for these answers).
PRESETS = {
    "default": dict(rules=DEFAULT_RULES, speed_guard=SPEED_GUARD, options={}),
    "trackb": dict(rules=("facts", "motionfam", "freefall", "labfacts", "pool"), speed_guard=0.0,
                   options={"motionfam": {"guard": 0.0}, "pool": {"unit": "base", "max_dev": 1.6}}),
}


@dataclass(frozen=True)
class Spec:
    kind: str
    objs: tuple
    dim: str
    time: float | None
    window: tuple | None
    axis: str
    to_si: float | None          # factor from the question's unit to SI (None: unit does not fit the kind)


def _spec(row) -> Spec:
    from qp.open.qwen_vl import parse_question_text

    t = parse_question_text(row.question)
    kind = t["kind"]
    objs = tuple(o for o in (_clean_object(x) for x in t["objects"]) if o)
    to_si = None
    if kind in DIM_OF_KIND:
        u = canonical_unit(str(row.target_unit or "")) if row.target_unit else None
        if u is None:
            to_si = 1.0
        elif u in _UNITS and _UNITS[u][1] == DIM_OF_KIND[kind]:
            to_si = float(_UNITS[u][0])
    dim = _DIM_SYN.get(t["dimension"], t["dimension"]) if kind == "size" else ""
    return Spec(kind, objs, dim, t["time"], tuple(t["window"]) if t["window"] else None, t["axis"], to_si)


class _Ctx:
    """Family structure of a question table, computed once and shared by the rules."""

    def __init__(self, df: pd.DataFrame, frames: FrameCache | None):
        self.df = df
        self.facts = _parse_facts(df)
        self.links = scene_links(df, self.facts, frames)
        self.fam_size = scene_families(df, self.links, SIZE_LINKS)
        self.fam_motion = scene_families(df, self.links, MOTION_LINKS)
        self.scen = scene_families(df, self.links, ("render", "scenario"))
        self.accel = _accel_objects(df, self.facts)
        self.depth = {v: _depth_entries(di) for v, di in zip(df.video_id, df.depth_info)}
        self.row = {int(r.qid): r for r in df.itertuples()}
        self.spec = {q: _spec(r) for q, r in self.row.items()}


def _objs_match(a: tuple, b: tuple, min_name: float = MIN_NAME) -> bool:
    if len(a) != len(b) or not a:
        return False
    if len(a) == 1:
        return _same_object(a[0], b[0]) >= min_name
    if len(a) == 2:
        return ((_same_object(a[0], b[0]) >= min_name and _same_object(a[1], b[1]) >= min_name) or
                (_same_object(a[0], b[1]) >= min_name and _same_object(a[1], b[0]) >= min_name))
    return False


def _same_motion(ctx: _Ctx, va: str, vb: str, sa: Spec, sb: Spec) -> bool:
    """Same moving event: one base clip (twin / lab renders), one scenario (identical render or identical motion
    prior in one family), or identical timed depth entries of the object."""
    if base_id(va) == base_id(vb) or ctx.scen[va] == ctx.scen[vb]:
        return True
    return all(_depth_identical(ctx.depth[va], ctx.depth[vb], oa, ob) for oa, ob in zip(sa.objs, sb.objs))


def equivalent_questions(ctx: _Ctx, qids=None) -> dict[int, list[int]]:
    """qid -> other qids asking the same quantity of the same object(s) in the scene family (pool rule):
    same kind / dimension / time / window / axis, names matching (head noun, name_score >= MIN_NAME; both
    objects for a distance); sizes within one base clip or across simulation clips of one family; motion and
    distances only within one moving event (_same_motion)."""
    keyed = defaultdict(list)
    for q, s in ctx.spec.items():
        if s.kind not in POOL_KINDS or s.to_si is None or not s.objs:
            continue
        r = ctx.row[q]
        fam = ctx.fam_size[r.video_id] if s.kind == "size" else ctx.fam_motion[r.video_id]
        keyed[(fam, s.kind, s.dim, s.time, s.window, s.axis, len(s.objs))].append(q)
    want = None if qids is None else set(qids)
    out: dict[int, list[int]] = {}
    for qs in keyed.values():
        if len(qs) < 2:
            continue
        for a, b in itertools.combinations(qs, 2):
            if want is not None and a not in want and b not in want:
                continue
            ra, rb = ctx.row[a], ctx.row[b]
            sa, sb = ctx.spec[a], ctx.spec[b]
            if not _objs_match(sa.objs, sb.objs):
                continue
            if sa.kind == "size":
                if not (base_id(ra.video_id) == base_id(rb.video_id) or
                        (is_simulation(ra.video_id) and is_simulation(rb.video_id))):
                    continue
            elif not _same_motion(ctx, ra.video_id, rb.video_id, sa, sb):
                continue
            out.setdefault(a, []).append(b)
            out.setdefault(b, []).append(a)
    return out


def pooled_value(logs, tau: float = POOL_TAU, cap2: float = POOL_CAP2, smax: float = POOL_SMAX):
    """Pool of log votes (one per clip) or None (no change): 2 votes -> their mean when within cap2; >= 3 votes
    -> mean of the votes within tau of the median (the median when tau <= 0); <= 3 votes spread over more than
    smax -> None (identity or definition in doubt)."""
    v = np.asarray([x for x in logs if np.isfinite(x)], float)
    if len(v) < 2:
        return None
    if len(v) <= 3 and smax and np.ptp(v) > smax:
        return None
    if len(v) == 2:
        return float(v.mean()) if abs(v[0] - v[1]) <= cap2 else None
    m = float(np.median(v))
    if tau <= 0:
        return m
    keep = v[np.abs(v - m) <= tau]
    return float(keep.mean()) if len(keep) else m


def _pool_rule(cur, ctx: _Ctx, protected, log, cats=None, kinds=POOL_KINDS, unit="clip", tau=POOL_TAU,
               cap2=POOL_CAP2, smax=POOL_SMAX, max_mad=None, max_dev=None, sources=None, scope="family") -> None:
    """P: answers about one object / quantity / time in a scene family are pooled (one vote per clip, or per
    base clip with unit='base'); groups holding a stated-fact row are left to the facts. Optional guards:
    max_mad (skip when the votes' median absolute log deviation exceeds it: no consensus), max_dev (skip a row
    whose own vote is more than max_dev x off the pool: likely another object or definition), sources (only
    rows of these video sources change), scope='base' (pool only within one base clip: a segmented twin and
    its original, the s/x renders of one lab event)."""
    snap = cur.copy()
    eq = equivalent_questions(ctx, [q for q in cur.index if q in ctx.row])
    for q in sorted(eq):
        if q not in cur.index or q in protected:
            continue
        r, s = ctx.row[q], ctx.spec[q]
        if s.kind not in kinds or (cats is not None and r.category not in cats):
            continue
        if sources is not None and r.video_source not in sources:
            continue
        members = [q] + [p for p in eq[q] if p in snap.index and
                         (scope != "base" or base_id(ctx.row[p].video_id) == base_id(r.video_id))]
        if any(p in protected for p in members):
            continue
        votes = defaultdict(list)
        for p in members:
            if _finite_pos(snap[p]):
                v = ctx.row[p].video_id
                votes[v if unit == "clip" else base_id(v)].append(math.log(float(snap[p]) * ctx.spec[p].to_si))
        if not _finite_pos(snap[q]) or len(votes) < 2:
            continue
        vl = [float(np.mean(x)) for x in votes.values()]
        if max_mad is not None and float(np.median(np.abs(np.array(vl) - np.median(vl)))) > max_mad:
            continue
        pv = pooled_value(vl, tau, cap2, smax)
        if pv is None:
            continue
        own_key = r.video_id if unit == "clip" else base_id(r.video_id)
        if max_dev and abs(float(np.mean(votes[own_key])) - pv) > math.log(max_dev):
            continue
        new = math.exp(pv) / s.to_si
        old = float(cur[q])
        if math.isclose(new, old, rel_tol=1e-12):
            continue
        cur[q] = new
        src = sorted({ctx.row[p].video_id for p in members} - {r.video_id})
        log.append(dict(qid=q, rule="pool", old=old, new=new, source_qid=math.nan, source_clip=",".join(src),
                        applied=True, reason=f"pooled {len(votes)} clip votes ({s.kind} of {' / '.join(s.objs)})"))


def _lab_key_groups(ctx: _Ctx):
    """Lab size questions about one prop across events: [(qids, dimension)] with >= 2 events."""
    lab = [q for q, s in ctx.spec.items() if s.kind == "size" and s.to_si is not None and len(s.objs) == 1
           and str(ctx.row[q].video_id).startswith("captured_")]
    uf = _UF()
    for q in lab:
        uf.find(q)
    for a, b in itertools.combinations(lab, 2):
        sa, sb = ctx.spec[a], ctx.spec[b]
        if sa.dim == sb.dim and _same_object(sa.objs[0], sb.objs[0]) >= LAB_NAME:
            uf.union(a, b)
    groups = defaultdict(list)
    for q in lab:
        groups[uf.find(q)].append(q)
    return [g for g in groups.values() if len({base_id(ctx.row[q].video_id) for q in g}) >= 2]


def _lab_facts(ctx: _Ctx) -> list[Fact]:
    return [f for f in ctx.facts if f.kind == "size" and str(f.video_id).startswith("captured_")]


def _labfacts_rule(cur, ctx: _Ctx, protected, log, cats=None) -> set[int]:
    """LAB facts: a lab size question about a prop whose size another lab event STATES (same dimension, name
    score >= LAB_NAME with the same head noun; the props are reused across events: basketball, tennis ball, ...)
    takes the stated value; conflicting statements -> skipped."""
    applied = set()
    facts = _lab_facts(ctx)
    for q, s in ctx.spec.items():
        r = ctx.row[q]
        if q not in cur.index or q in protected or s.kind != "size" or s.to_si is None or len(s.objs) != 1:
            continue
        if not str(r.video_id).startswith("captured_") or (cats is not None and r.category not in cats):
            continue
        own = {norm_ws(x) for x in str(r.prior).split("\n")}
        hit = [f for f in facts if f.dimension == s.dim and _same_object(s.objs[0], f.obj) >= LAB_NAME
               and not (f.video_id == r.video_id and norm_ws(f.line) in own)]
        if not hit:
            continue
        vals = sorted({round(f.si, 9) for f in hit})
        src = ",".join(sorted({f.video_id for f in hit}))
        old = float(cur[q])
        if len(vals) != 1:
            log.append(dict(qid=q, rule="labfacts", old=old, new=math.nan, source_qid=math.nan, source_clip=src,
                            applied=False, reason="skipped: lab events state conflicting values"))
            continue
        new = vals[0] / s.to_si
        cur[q] = new
        applied.add(q)
        log.append(dict(qid=q, rule="labfacts", old=old, new=new, source_qid=math.nan, source_clip=src, applied=True,
                        reason=f"lab prop size stated by {src}: '{hit[0].line}'"))
    return applied


def _labpool_rule(cur, ctx: _Ctx, protected, log, cats=None, spread2=LAB_SPREAD2, max_dev=LAB_DEV) -> None:
    """LAB pooling: sizes of one lab prop asked in several events. Event value = log-median of its renders'
    answers (SI); a row takes the log-median of the other events' values and its own event's. Skipped: groups
    with a stated-fact row, 2-event groups whose values differ > spread2 x, rows whose event is > max_dev x off
    the other events' median when >= 2 others (likely a different object of the same name)."""
    snap = cur.copy()
    for g in _lab_key_groups(ctx):
        g = [q for q in g if q in snap.index and _finite_pos(snap[q])]
        if any(q in protected for q in g):
            continue
        ev = defaultdict(list)
        for q in g:
            ev[base_id(ctx.row[q].video_id)].append(math.log(float(snap[q]) * ctx.spec[q].to_si))
        if len(ev) < 2:
            continue
        evv = {b: float(np.median(x)) for b, x in ev.items()}
        if len(evv) == 2 and spread2 and np.ptp(list(evv.values())) > math.log(spread2):
            continue
        for q in g:
            r = ctx.row[q]
            if cats is not None and r.category not in cats:
                continue
            b = base_id(r.video_id)
            others = [v for k, v in evv.items() if k != b]
            if max_dev and len(others) >= 2 and abs(evv[b] - float(np.median(others))) > math.log(max_dev):
                continue
            new = math.exp(float(np.median(others + [evv[b]]))) / ctx.spec[q].to_si
            old = float(cur[q])
            if math.isclose(new, old, rel_tol=1e-12):
                continue
            cur[q] = new
            log.append(dict(qid=q, rule="labpool", old=old, new=new, source_qid=math.nan,
                            source_clip=",".join(sorted(k for k in evv if k != b)), applied=True,
                            reason=f"lab prop pooled over {len(evv)} events ({ctx.spec[q].dim} of {ctx.spec[q].objs[0]})"))


_MOTION_ADJ = re.compile(r"\b(?:moving|walking|running|flying)\s+", re.I)


def _mf_name(s: str) -> str:
    return _MOTION_ADJ.sub("", re.sub(r"\bbicycle\b", "bike", str(s), flags=re.I)).strip()


def _mf_match(a: str, b: str) -> bool:
    a, b = _mf_name(a), _mf_name(b)
    return bool(_head(a)) and _same_object(a, b) >= MIN_NAME


def _radial_speed(depth: dict, obj: str):
    best = None
    for k, e in depth.items():
        te = [x for x in e if x[0] is not None]
        if len(te) >= 2 and (_mf_match(k, obj) or name_score(k, obj) >= 0.6):
            best = te
    if best is None:
        return math.nan, None
    (t0, r0), (t1, r1) = best[0], best[-1]
    return (abs(r1 - r0) / (t1 - t0) if t1 > t0 else math.nan), tuple(best)


def _motionfam_rule(cur, ctx: _Ctx, protected, log, cats=("S3", "D3"), guard=SPEED_GUARD) -> set[int]:
    """MF (research/sim3d): a speed / acceleration question about object O in a simulation clip takes the value
    another simulation clip of the same scene family (size links: one Blender scene) STATES for O, when the
    statements agree within 2% (log-mean), the timing fits (untimed, or stated at the asked time without a
    window), a speed's O has no acceleration stated or asked in either clip, and every family clip with a timed
    depth track of O moves radially no faster than 1.05 x the stated speed (one constant-speed event). A value
    > guard x off the current answer is skipped unless the asking clip has the stating clip's depth track."""
    applied = set()
    by_fam = defaultdict(list)
    for f in ctx.facts:
        if f.kind in ("speed", "acceleration") and is_simulation(f.video_id):
            by_fam[ctx.fam_size[f.video_id]].append(f)
    clips_of = defaultdict(set)
    for v in ctx.df.video_id:
        clips_of[ctx.fam_size[v]].add(v)
    for q, s in ctx.spec.items():
        r = ctx.row[q]
        if q not in cur.index or q in protected or s.kind not in ("speed", "acceleration") or len(s.objs) != 1:
            continue
        if not is_simulation(r.video_id) or s.to_si is None or (cats is not None and r.category not in cats):
            continue
        obj = s.objs[0]
        own = {norm_ws(x) for x in str(r.prior).split("\n")}
        cands = []
        for f in by_fam[ctx.fam_size[r.video_id]]:
            if f.kind != s.kind or not _mf_match(obj, f.obj):
                continue
            if f.video_id == r.video_id and norm_ws(f.line) in own:
                continue
            if f.timed and (s.window is not None or s.time is None or f.time is None or abs(s.time - f.time) > 1e-6):
                continue
            if s.kind == "speed" and any(_mf_match(obj, o) for v in (r.video_id, f.video_id)
                                         for o in ctx.accel.get(v, [])):
                continue
            cands.append(f)
        if not cands:
            continue
        vals = np.array([f.si for f in cands])
        if vals.max() / vals.min() > 1 + MF_AGREE:
            continue
        v_si = float(np.exp(np.log(vals).mean()))
        ok, same_track = True, False
        _, own_track = _radial_speed(ctx.depth[r.video_id], obj)
        for c in sorted(clips_of[ctx.fam_size[r.video_id]]):
            vr, tr = _radial_speed(ctx.depth[c], obj)
            if s.kind == "speed" and math.isfinite(vr) and vr > MF_RADIAL * v_si:
                ok = False
            if own_track is not None and tr == own_track and c != r.video_id and \
                    any(base_id(f.video_id) == base_id(c) for f in cands):
                same_track = True
        if not ok:
            continue
        new = v_si / s.to_si
        old = float(cur[q])
        src = ",".join(sorted({f.video_id for f in cands}))
        if guard and _finite_pos(old) and max(new / old, old / new) > guard and not same_track:
            log.append(dict(qid=q, rule="motionfam", old=old, new=new, source_qid=math.nan, source_clip=src,
                            applied=False, reason=f"skipped: stated value >{guard:g}x off the clip's own answer"))
            continue
        cur[q] = new
        applied.add(q)
        log.append(dict(qid=q, rule="motionfam", old=old, new=new, source_qid=math.nan, source_clip=src, applied=True,
                        reason=f"scene family states '{'; '.join(sorted({f.line for f in cands}))}'"))
    return applied


def free_fall(path: str, t: float, fps: float, max_frames: int = 40) -> bool:
    """Do the frames show a vertical fall from rest through frame round(t * fps)? (moving region's lower edge
    with positive, growing steps, no horizontal drift; research/sim3d FF)."""
    import cv2

    k = int(round(t * fps))
    if k < 3:
        return False
    cap = cv2.VideoCapture(str(path))
    fr = []
    while len(fr) < min(max_frames, k + 3):
        ok, f = cap.read()
        if not ok:
            break
        fr.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.int16))
    cap.release()
    if k + 2 >= len(fr):
        return False
    ymax, xmed = [], []
    for i in range(1, k + 2):
        ys, xs = np.nonzero(np.abs(fr[i] - fr[i - 1]) > 25)
        if len(ys) < 50:
            return False
        ymax.append(ys.max())
        xmed.append(np.median(xs))
    d1 = np.diff(ymax)
    d2 = np.diff(d1)
    w = fr[0].shape[1]
    return bool((d1 > 0).all() and np.median(d2) > 0.5 and (d2 > -2).all() and np.ptp(xmed[1:]) < 0.03 * w)


def _freefall_rule(cur, ctx: _Ctx, protected, log, frames: FrameCache | None, cats=("S3", "D3")) -> set[int]:
    """FF: an acceleration asked at time t in a 3D simulation clip whose frames show a vertical fall from rest
    through that frame takes 9.8 m/s^2 (Blender labels; the test priors state free-fall phases as 9.8)."""
    applied = set()
    if frames is None:
        return applied
    for q, s in ctx.spec.items():
        r = ctx.row[q]
        if q not in cur.index or q in protected or s.kind != "acceleration" or s.time is None or s.to_si is None:
            continue
        if not is_simulation(r.video_id) or (cats is not None and r.category not in cats) or not r.video_path:
            continue
        fps = float(getattr(r, "fps", math.nan) or math.nan)
        if not math.isfinite(fps) or not math.isfinite(s.time):
            continue
        if not frames.free_fall(r.video_id, r.video_path, s.time, fps):
            continue
        old = float(cur[q])
        new = G_EARTH / s.to_si
        cur[q] = new
        applied.add(q)
        log.append(dict(qid=q, rule="freefall", old=old, new=new, source_qid=math.nan, source_clip=r.video_id,
                        applied=True, reason=f"frames show a vertical fall from rest through t={s.time:g}s"))
    return applied


def _kscale_rule(cur, ctx: _Ctx, protected, fact_log: list[dict], log, cats=("D3",), kinds=K_KINDS) -> None:
    """K: a clip whose answers missed the values its family states (fact rows: log(stated / answer before the
    fact)) has the other size / speed answers rescaled by median({0} U those log ratios) (Track A: D3 only;
    the error is a per-clip scale shared across quantities)."""
    lk = defaultdict(list)
    for e in fact_log:
        q = int(e["qid"])
        if e.get("applied") and q in ctx.spec and ctx.spec[q].kind in kinds and _finite_pos(e["old"]) and _finite_pos(e["new"]):
            lk[ctx.row[q].video_id].append(math.log(float(e["new"]) / float(e["old"])))
    for v, ls in sorted(lk.items()):
        k = float(np.median([0.0] + ls))
        if abs(k) < 1e-9:
            continue
        for q in ctx.df.qid[ctx.df.video_id == v]:
            q = int(q)
            r, s = ctx.row[q], ctx.spec[q]
            if q not in cur.index or q in protected or s.kind not in kinds or not _finite_pos(cur[q]):
                continue
            if cats is not None and r.category not in cats:
                continue
            old = float(cur[q])
            cur[q] = old * math.exp(k)
            log.append(dict(qid=q, rule="kscale", old=old, new=float(cur[q]), source_qid=math.nan, source_clip=v,
                            applied=True, reason=f"clip scale x{math.exp(k):.3f} from {len(ls)} stated fact(s)"))


# ----------------------------------------------------------------------------- entry point

def apply_rules(pred: pd.Series, test_df: pd.DataFrame, rules=DEFAULT_RULES, video_root=None, cache_dir=DEFAULT_CACHE,
                render_mask: pd.Series | None = None, speed_guard: float = SPEED_GUARD,
                use_frames: bool = True, options: dict | None = None) -> tuple[pd.Series, pd.DataFrame]:
    """Apply the rules to `pred` (answers indexed by qid) -> (new answers, log).

    test_df: question table (qp.data.load_split columns: qid, video_id, video_path, question, prior,
        depth_info, category, target_unit ...); answers in it are ignored.
    rules: any of RULES, always applied in the order facts, motionfam, freefall, labfacts (stated values;
        these rows are protected from the later rules), kscale, pool, labpool, render, twin. The default is
        the original three (DEFAULT_RULES).
    video_root: folder of the .mp4 files (default: test_df.video_path).
    render_mask: optional bool Series by qid; the render rule only replaces rows where it is True.
    use_frames: False skips every frame-based check (twins are then never copied; no frame links, no free fall).
    options: per-rule settings, e.g. {"pool": {"cats": ("D2", "D3"), "tau": 0.15, "unit": "clip"},
        "kscale": {"cats": ("D3",)}, "labpool": {...}, "labfacts": {...}, "motionfam": {"guard": 2.0},
        "freefall": {"cats": ("S3", "D3")}} (keyword arguments of the _<rule>_rule functions).
    log: one row per decision (qid, rule, old, new, source_qid, source_clip, reason, applied); rows with
        applied=False record guarded skips."""
    unknown = set(rules) - set(RULES)
    if unknown:
        raise ValueError(f"unknown rules {sorted(unknown)} (expected some of {RULES})")
    opt = {k: dict(v) for k, v in (options or {}).items()}
    bad = set(opt) - set(RULES)
    if bad:
        raise ValueError(f"options for unknown rules {sorted(bad)}")
    cur = pd.Series(pred, dtype=float).copy()
    cur.index = cur.index.astype(int)
    df = _questions(test_df, video_root)
    frames = FrameCache(cache_dir) if use_frames else None
    log: list[dict] = []
    protected: set[int] = set()
    try:
        if "facts" in rules:
            protected = _facts_rule(cur, df, frames, log, speed_guard)
        ctx = _Ctx(df, frames) if set(rules) & set(EXTENDED_RULES) else None
        if "motionfam" in rules:
            protected |= _motionfam_rule(cur, ctx, protected, log, **opt.get("motionfam", {}))
        if "freefall" in rules:
            protected |= _freefall_rule(cur, ctx, protected, log, frames, **opt.get("freefall", {}))
        if "labfacts" in rules:
            protected |= _labfacts_rule(cur, ctx, protected, log, **opt.get("labfacts", {}))
        if "kscale" in rules:
            fact_log = [e for e in log if e["rule"] in ("facts", "motionfam")]
            _kscale_rule(cur, ctx, protected, fact_log, log, **opt.get("kscale", {}))
        if "pool" in rules:
            _pool_rule(cur, ctx, protected, log, **opt.get("pool", {}))
        if "labpool" in rules:
            _labpool_rule(cur, ctx, protected, log, **opt.get("labpool", {}))
        if "render" in rules:
            eligible = None
            if render_mask is not None:
                m = pd.Series(render_mask).astype(bool)
                m.index = m.index.astype(int)
                eligible = lambda q: bool(m.get(q, False))  # noqa: E731
            _render_rule(cur, df, protected, log, eligible)
        if "twin" in rules:
            _twin_rule(cur, df, frames, protected, log)
    finally:
        if frames is not None:
            frames.save()
    out = pd.DataFrame(log, columns=LOG_COLUMNS)
    return cur, out


def summary(log: pd.DataFrame, df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Applied / changed / skipped counts per rule (and category when `df` is given)."""
    if log.empty:
        return pd.DataFrame(columns=["rule", "applied", "changed", "skipped"])
    x = log.copy()
    x["changed"] = x.applied & ~np.isclose(x.new.astype(float), x.old.astype(float), rtol=1e-9, equal_nan=False)
    keys = ["rule"]
    if df is not None:
        x["category"] = x.qid.map(dict(zip(df.qid.astype(int), df.category)))
        keys.append("category")
    g = x.groupby(keys)
    return pd.DataFrame({"applied": g.applied.sum(), "changed": g.changed.sum(),
                         "skipped": g.applied.agg(lambda s: int((~s).sum()))}).reset_index()
