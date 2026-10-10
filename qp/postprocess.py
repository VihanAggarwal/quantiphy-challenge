"""Model-free post-processing of test predictions from the structure of the test inputs.

    from qp.postprocess import apply_rules
    new, log = apply_rules(pred, test_df)          # pred: Series of answers indexed by qid

Three rules, ported from the Track A probes (research/PROBES.md, probes 4 and 5). They read only test
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
        Not ported (Claude-specific or speculative): per-clip scale correction, pooling, lab kind split,
        single-clip data fixes.

Order: facts, then render, then twin, so an s/x render or a segmented twin copies its source's FINAL
answer; a row that received its own stated fact keeps it. Frame-based links are cached under
runs/_postprocess_cache/ (keyed by file size and mtime), so a re-run is fast.
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
RULES = ("twin", "render", "facts")
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
        self._dirty = False
        if not self.dir:
            return
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

    def save(self) -> None:
        if not (self.dir and self._dirty):
            return
        self.dir.mkdir(parents=True, exist_ok=True)
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


# ----------------------------------------------------------------------------- entry point

def apply_rules(pred: pd.Series, test_df: pd.DataFrame, rules=RULES, video_root=None, cache_dir=DEFAULT_CACHE,
                render_mask: pd.Series | None = None, speed_guard: float = SPEED_GUARD,
                use_frames: bool = True) -> tuple[pd.Series, pd.DataFrame]:
    """Apply the rules to `pred` (answers indexed by qid) -> (new answers, log).

    test_df: question table (qp.data.load_split columns: qid, video_id, video_path, question, prior,
        depth_info, category, target_unit ...); answers in it are ignored.
    rules: any of "twin", "render", "facts" (always applied in the order facts, render, twin).
    video_root: folder of the .mp4 files (default: test_df.video_path).
    render_mask: optional bool Series by qid; the render rule only replaces rows where it is True.
    use_frames: False skips every frame-based check (twins are then never copied; no frame links).
    log: one row per decision (qid, rule, old, new, source_qid, source_clip, reason, applied); rows with
        applied=False record guarded skips."""
    unknown = set(rules) - set(RULES)
    if unknown:
        raise ValueError(f"unknown rules {sorted(unknown)} (expected some of {RULES})")
    cur = pd.Series(pred, dtype=float).copy()
    cur.index = cur.index.astype(int)
    df = _questions(test_df, video_root)
    frames = FrameCache(cache_dir) if use_frames else None
    log: list[dict] = []
    protected: set[int] = set()
    try:
        if "facts" in rules:
            protected = _facts_rule(cur, df, frames, log, speed_guard)
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
