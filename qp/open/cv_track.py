"""CV tracks (Track B): text-prompted detection on keyframes + SAM 2 video propagation -> RoleTracks.

    from qp.open.cv_track import CVTracker
    trk = CVTracker(detector="gdino", segmenter="auto")      # models load on first use (GPU)
    rec, cache = trk.track_video(rows_of_one_video, specs, cache)   # specs: {qid: QuestionSpec}
    rec["tracks"][str(qid)]                                  # [RoleTrack dicts] for qp.geometry.solve

Per video:
1. Objects: one per distinct noun phrase over the video's specs (roles prior / prior2 / target /
   target2; generic names such as "gravity" or "camera" are skipped). The same phrase for a role and
   its "2" partner ("distance between the two black cars") is two instances, ordered left to right.
2. Detection: Grounding DINO (IDEA-Research/grounding-dino-base, primary) or OWLv2
   (google/owlv2-base-patch16-ensemble) on `n_keyframes` uniform frames plus the frames at times the
   specs mention. The query is the phrase's head chunk without spatial words ("white car in the
   roundabout" -> "white car").
3. Instance + keyframe: per frame, candidates are re-ranked by colour words (HSV share of the box
   centre), spatial words (left/right/top/bottom/center/front/back/big/small, ordinals "second
   from the left") and by not re-using the keyframe box of an object of the same head noun told
   apart by conflicting words ("purple ball" vs "black ball"; a bare "ball" conflicts with none).
   The keyframe is the frame with the best re-ranked score (frames showing every instance preferred
   when the choice is relational).
4. SAM 2 (facebook/sam2.1-hiera-large; official `sam2` package, else - not installed or failing to
   load - transformers' Sam2Video) is prompted with each object's box on its keyframe and propagated
   forward and backward. A model that fails to load raises ModelLoadError for every later video.
5. Measurements per mask (pure numpy/cv2, see `mask_features` / `extent_from_features`).

Measurement conventions. Pixel (row i, col j) is the square [j, j+1) x [i, i+1): box =
[xmin, ymin, xmax + 1, ymax + 1] and lengths run edge to edge (a 10-pixel-wide mask is 10 px wide).
Components smaller than 10% of the largest are dropped first.
  point     mask centroid (pixel centres); point_mode "bottom" = bottom-centre (feet), "top"
  extent by the asked dimension (`dimension_mode`):
    height / tall / vertical      vertical span of the mask at the centroid's x
    width / breadth / horizontal  horizontal span at the centroid's y (width of upright objects such
                                  as doors or people is horizontal; the major axis would be height)
    thickness / thin              short side of the minimum-area rotated rectangle
    length / span / size / other  long side of the minimum-area rotated rectangle (major axis)
    diameter                      round mask (long/short <= 1.25 and filling < 0.88 of its rotated
                                  rectangle; a disc fills pi/4): equivalent-circle diameter
                                  sqrt(4 A / pi); otherwise short side for spheres (motion blur)
                                  and cylinders (a cup / tube seen from the side: its width), long
                                  side for the rest (a wheel / plate seen obliquely is a
                                  foreshortened disc)
    radius                        half the diameter, from the centroid
    calibre / graduation of a ruler, tape or scale: no track for that role (the marks' spacing is
                                  not a mask dimension; geometry then fails and the direct answer
                                  is used)
  Frames whose mask touches the image border lose point and extent (kept: box) when the track has
  enough untouched frames; frames whose area jumps by > 2.5x against a running median are dropped.
  Obs.score = mask confidence (mean sigmoid inside the mask) x the keyframe detection score.

Detections and per-frame mask features are cached per video (a JSON-able dict), so new specs or
another dimension reuse earlier SAM 2 runs; masks themselves are not stored.
torch / transformers / sam2 are imported inside the model classes only.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np

from qp.claude_annotate import to_annotations, video_fps
from qp.spec import Obs, Quantity, QuestionSpec, RoleTrack

DETECTOR_MODELS = {"gdino": "IDEA-Research/grounding-dino-base",
                   "owlv2": "google/owlv2-base-patch16-ensemble"}
DET_THRESHOLD = {"gdino": 0.25, "owlv2": 0.1}
SAM_MODEL = "facebook/sam2.1-hiera-large"
MAX_FRAMES = 360          # frames tracked per video (longer videos use every k-th frame)
N_KEYFRAMES = 8           # uniform detection frames (plus frames at mentioned times, max 12)
REL_KEEP = 0.5            # a candidate must reach this share of the frame's best re-ranked score
NMS_IOU = 0.6
AREA_JUMP = 2.5           # drop frames whose area differs by more than this factor from the running median
CACHE_VERSION = 1

# --------------------------------------------------------------------------- mask measurement

_CORNERS = np.array([[0, 0], [1, 0], [0, 1], [1, 1]], np.float32)


def clean_mask(mask: np.ndarray, min_frac: float = 0.1) -> np.ndarray:
    """Boolean mask without connected components smaller than `min_frac` of the largest one."""
    m = np.asarray(mask, bool)
    if not m.any():
        return m
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
    if n <= 2:
        return m
    areas = stats[1:, cv2.CC_STAT_AREA]
    return np.isin(lab, np.flatnonzero(areas >= min_frac * areas.max()) + 1)


def min_area_rect(mask: np.ndarray) -> list[float]:
    """[cx, cy, long side, short side, angle of the long side in radians in [0, pi)] of the smallest
    rotated rectangle around the mask's pixel squares (not their centres)."""
    contours, _ = cv2.findContours(np.asarray(mask, np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    pts = np.concatenate([c.reshape(-1, 2) for c in contours]).astype(np.float32)
    corners = (pts[:, None, :] + _CORNERS[None]).reshape(-1, 2)
    rect = cv2.minAreaRect(corners)
    p = cv2.boxPoints(rect)
    e0, e1 = p[1] - p[0], p[2] - p[1]
    l0, l1 = float(np.hypot(*e0)), float(np.hypot(*e1))
    e = e0 if l0 >= l1 else e1
    return [float(rect[0][0]), float(rect[0][1]), max(l0, l1), min(l0, l1),
            float(math.atan2(e[1], e[0]) % math.pi)]


def mask_features(mask: np.ndarray, clean: bool = True) -> dict | None:
    """Geometry of one mask (None if empty): box, centroid c, area, min-area rect, edge (touches
    the image border). Rounded to 0.01 px so it can be cached as JSON."""
    m = np.asarray(mask, bool)
    rows, cols = np.flatnonzero(m.any(axis=1)), np.flatnonzero(m.any(axis=0))
    if not len(rows):
        return None
    y0, y1, x0, x1 = int(rows[0]), int(rows[-1]) + 1, int(cols[0]), int(cols[-1]) + 1
    crop = m[y0:y1, x0:x1]
    if clean:
        crop = clean_mask(crop)
        r2, c2 = np.flatnonzero(crop.any(axis=1)), np.flatnonzero(crop.any(axis=0))
        crop = crop[r2[0]:r2[-1] + 1, c2[0]:c2[-1] + 1]
        y0, x0 = y0 + int(r2[0]), x0 + int(c2[0])
        y1, x1 = y0 + crop.shape[0], x0 + crop.shape[1]
    ys, xs = np.nonzero(crop)
    rect = min_area_rect(crop)
    rect[0] += x0
    rect[1] += y0
    H, W = m.shape
    r = lambda v: round(float(v), 2)  # noqa: E731
    return {"box": [x0, y0, x1, y1], "c": [r(xs.mean() + 0.5 + x0), r(ys.mean() + 0.5 + y0)],
            "area": int(len(xs)), "rect": [r(v) for v in rect[:4]] + [round(rect[4], 4)],
            "edge": bool(x0 == 0 or y0 == 0 or x1 == W or y1 == H)}


_SPHERE = re.compile(r"balls?\b|\bball?oo?ns?\b|\b(?:spheres?|globes?|planets?|moons?|marbles?|bubbles?|drops?|"
                     r"droplets?|orbs?|beads?|apples?|melons?|watermelons?|grapes?|eggs?|jupiter|io|europa|"
                     r"ganymede|callisto|earth|mars|saturn)\b", re.I)   # "basketball" yes, "ballerina" no
_CYLINDER = re.compile(r"\b(?:tubes?|pipes?|rods?|poles?|cylinders?|bottles?|cans?|cups?|glass|jars?|mugs?|vases?|"
                       r"buckets?|barrels?|straws?|wires?|sticks?|pencils?|pens?|columns?|pillars?|posts?|trunks?|"
                       r"hoses?|cables?|bars?|shafts?|axles?|candles?|towers?|chimneys?)\b", re.I)
_GRADUATION = re.compile(r"calib|graduat|\bticks?\b|\bdivisions?\b|\bmarks?\b|\bmarkings?\b|\bintervals?\b|spacing")
_MEASURING = re.compile(r"\b(?:rulers?|scales?|tapes?|measur\w*|met(?:er|re) ?sticks?|yardsticks?|calipers?)\b")
ROUND_FILL = 0.88         # a mask filling less of its rotated rectangle is round (disc: pi/4, rectangle: 1)


@lru_cache(maxsize=4096)
def is_sphere(name: str) -> bool:
    """Round object by name; "orange" only as the head noun ("an orange", not "orange car")."""
    if _SPHERE.search(name or ""):
        return True
    q = parse_phrase(name).query.split() if name else []
    return bool(q) and q[-1] in ("orange", "oranges")


def dimension_mode(dimension: str, name: str = "") -> str | None:
    """'vertical' | 'horizontal' | 'major' | 'minor' | 'diameter' | 'radius' for a size dimension;
    None for the calibre / graduation of a measuring tool ("ruler calibre = 1cm")."""
    d, n = str(dimension or "").lower(), str(name or "").lower()
    if _GRADUATION.search(f"{d} {n}") and _MEASURING.search(f"{d} {n}"):
        return None
    if "radius" in d:
        return "radius"
    if re.search(r"diam|calib|caliber|circular|round", d):
        return "diameter"
    if re.search(r"height|tall|high|vertical|elevation", d):
        return "vertical"
    if re.search(r"width|wide|breadth|horizontal|across", d):
        return "horizontal"
    if re.search(r"thick|thin|minor|narrow", d):
        return "minor"
    if re.fullmatch(r"\s*(size|)\s*", d) and is_sphere(name):
        return "diameter"   # "size of the ball"
    return "major"


def _axis_extent(cx: float, cy: float, length: float, theta: float) -> list[list[float]]:
    dx, dy = 0.5 * length * math.cos(theta), 0.5 * length * math.sin(theta)
    return [[cx - dx, cy - dy], [cx + dx, cy + dy]]


def extent_from_features(f: dict, mode: str, name: str = "") -> list[list[float]]:
    """Endpoints [[x1, y1], [x2, y2]] of the dimension `mode` (see `dimension_mode`)."""
    x0, y0, x1, y1 = f["box"]
    cx, cy = f["c"]
    rx, ry, L, S, th = f["rect"]
    if mode == "vertical":
        return [[cx, float(y0)], [cx, float(y1)]]
    if mode == "horizontal":
        return [[float(x0), cy], [float(x1), cy]]
    if mode == "minor":
        return _axis_extent(rx, ry, S, th + math.pi / 2)
    if mode in ("diameter", "radius"):
        if L <= 1.25 * S and f["area"] < ROUND_FILL * L * S:
            d, ang = 2.0 * math.sqrt(f["area"] / math.pi), 0.0
        elif is_sphere(name) or _CYLINDER.search(name or ""):
            d, ang = S, th + math.pi / 2
        else:
            d, ang = L, th
        if mode == "radius":
            return [[cx, cy], [cx + 0.5 * d * math.cos(ang), cy + 0.5 * d * math.sin(ang)]]
        return _axis_extent(cx, cy, d, ang)
    return _axis_extent(rx, ry, L, th)


def point_from_features(f: dict, mode: str = "centroid") -> list[float]:
    cx, cy = f["c"]
    if mode == "bottom":
        return [cx, float(f["box"][3])]
    if mode == "top":
        return [cx, float(f["box"][1])]
    return [cx, cy]


def area_outliers(frames: list[int], areas: list[float], win: int = 7, jump: float = AREA_JUMP) -> set[int]:
    """Frames whose mask area differs by more than `jump`x from the median of the +-`win` neighbours
    (tracking glitches: the mask briefly jumps to another object or merges with it)."""
    a = np.log(np.maximum(np.asarray(areas, float), 1.0))
    bad = set()
    for i, f in enumerate(frames):
        nb = np.r_[a[max(0, i - win):i], a[i + 1:i + 1 + win]]
        if len(nb) >= 3 and abs(a[i] - np.median(nb)) > math.log(jump):
            bad.add(f)
    return bad


def build_obs(frames: dict, fps: float, extent_mode: str | None = None, name: str = "",
              point_mode: str = "centroid", det_score: float = 1.0) -> list[Obs]:
    """Obs per cached frame ({frame index: mask features}); t = frame index / fps. Area glitches
    are dropped; border-touching frames keep only the box if enough frames do not touch it."""
    fr = sorted((int(k), v) for k, v in frames.items() if v)
    if not fr:
        return []
    bad = area_outliers([k for k, _ in fr], [v["area"] for k, v in fr])
    fr = [(k, v) for k, v in fr if k not in bad]
    n_clear = sum(not v["edge"] for _, v in fr)
    drop_edge = n_clear >= max(5, 0.3 * len(fr))
    r = lambda p: [round(float(x), 1) for x in p]  # noqa: E731
    out = []
    for k, f in fr:
        ok = not (f["edge"] and drop_edge)
        ext = extent_from_features(f, extent_mode, name) if extent_mode and ok else None
        out.append(Obs(t=round(k / fps, 4), point=r(point_from_features(f, point_mode)) if ok else None,
                       extent=[r(p) for p in ext] if ext else None, box=[float(x) for x in f["box"]],
                       score=round(float(f.get("conf", 1.0)) * float(det_score), 3)))
    return out


# --------------------------------------------------------------------------- phrases and instances

COLORS = {"red": "red", "orange": "orange", "yellow": "yellow", "gold": "yellow", "golden": "yellow",
          "green": "green", "cyan": "cyan", "teal": "cyan", "turquoise": "cyan", "blue": "blue",
          "navy": "blue", "purple": "purple", "violet": "purple", "pink": "pink", "magenta": "pink",
          "brown": "brown", "white": "white", "black": "black", "gray": "gray", "grey": "gray",
          "silver": "gray"}
_SPATIAL = [  # (hint, pattern); relational uses ("right above", "in front of", "behind") excluded
    ("left", r"\bleft(?:most|-most)?\b"),
    ("right", (r"\bright(?:most|-most)?\b(?!\s+(?:above|below|over|under|next|behind|beside|in\s+front|on\s+top|"
               r"at|before|after|underneath|of\b))")),
    ("top", r"\b(?:top(?:most)?|upper(?:most)?|higher|highest)\b(?!\s+of\b)"),
    ("bottom", r"\b(?:bottom(?:most)?|lower|lowest)\b(?!\s+of\b)"),
    ("center", r"\b(?:cent(?:er|re|ral|ered|red)|middle)\b"),
    ("front", r"\b(?:front|foreground|nearest|closest|nearer|closer)\b(?!\s+of\b)"),
    ("back", r"\b(?:background|farthest|furthest|farther|rear|back)\b(?!\s+of\b)"),
    ("large", r"\b(?:big|bigger|biggest|large|larger|largest)\b"),
    ("small", r"\b(?:small|smaller|smallest|little|tiny)\b"),
]
_ORDINALS = {"first": 0, "1st": 0, "second": 1, "2nd": 1, "third": 2, "3rd": 2, "fourth": 3, "4th": 3,
             "fifth": 4, "5th": 4}
_PREP = re.compile(r"\s+(?:in|on|at|with|near|above|below|under|over|behind|beside|next\s+to|from|"
                   r"between|inside|around|along|across|into|onto|that|which|who|whose|where|while|"
                   r"standing|sitting|moving|located|placed)\s+")
_DROP = re.compile(r"\b(?:the|a|an|one|two|three|both|pair|side|corner|conrner|from|most)\b")
_DET = re.compile(r"the|a|an|his|her|its|their|some|this|that|these|those")
_GENERIC = re.compile(r"^(?:|g|gravity.*|.*\bgravit.*|camera|the camera|object|objects?|scene|unknown|none|"
                      r"n/?a|free ?fall|projectile|falling object|object in free fall)$", re.I)


@dataclass
class Hints:
    """What a noun phrase says about which instance it means."""
    query: str                                          # detector text, e.g. "white car"
    head: str                                           # head noun, e.g. "car"
    colors: list[str] = field(default_factory=list)     # canonical colour names
    spatial: list[str] = field(default_factory=list)    # hints from _SPATIAL
    ordinal: int | None = None                          # 0-based "second ..." along the spatial order

    def distinct_from(self, other: "Hints") -> bool:
        """Same kind of object told apart by conflicting words of the same type: colours ("purple
        ball" vs "black ball") or positions ("left" vs "right ball"). A phrase without such words
        ("tennis ball") may mean either instance, so it is distinct from none."""
        if self.head != other.head:
            return False
        if self.colors and other.colors and set(self.colors) != set(other.colors):
            return True
        placed = [h for h in (self, other) if h.spatial or h.ordinal is not None]
        return len(placed) == 2 and (set(self.spatial), self.ordinal) != (set(other.spatial), other.ordinal)


def color_word(w: str) -> str | None:
    """Canonical colour of a word, tolerating typos: transposed letters ("balck") or one dropped
    letter ("yelow") of a colour name of 5+ letters."""
    if w in COLORS:
        return COLORS[w]
    for c, canon in COLORS.items():
        if len(c) >= 5 and ((len(w) == len(c) and sorted(w) == sorted(c))
                            or (len(w) == len(c) - 1 and any(c[:i] + c[i + 1:] == w for i in range(len(c))))):
            return canon
    return None


def groundable(name: str) -> bool:
    return not _GENERIC.match(str(name or "").strip())


def object_key(phrase: str) -> tuple[str, int | None]:
    """(normalised key, 0-based instance from trailing numbering): "Black car 2" -> ("black car", 1)."""
    s = re.sub(r"[^a-z0-9#'\s-]", " ", str(phrase or "").lower())
    s = re.sub(r"'s\b", "", s)
    s = re.sub(r"\b(?:the|a|an)\b", " ", s)
    m = re.search(r"(?:\s+(?:no|number))?(?:\s+|\s*#\s*)(\d+)\s*$", s)
    inst = None
    if m and m.start() > 0:
        inst, s = max(int(m.group(1)) - 1, 0), s[:m.start()]
    return re.sub(r"\s+", " ", s).strip() or str(phrase).strip().lower(), inst


def parse_phrase(phrase: str) -> Hints:
    """Detector query, head noun, colour / spatial / ordinal words of an object phrase."""
    full = re.sub(r"\s+", " ", str(phrase or "").lower().replace("_", " ")).strip()
    full = re.sub(r"[’`]", "'", full)
    spatial = [h for h, pat in _SPATIAL if re.search(pat, full)]
    ordinal = next((v for k, v in _ORDINALS.items() if re.search(rf"\b{k}\b", full)), None)
    base = re.sub(r"\([^)]*\)", " ", full)
    base = re.sub(r"'s\b", "", base)
    base = re.sub(r"[^a-z0-9\s-]", " ", base)
    head_chunk = _PREP.split(f" {base} ", maxsplit=1)[0]
    words = [w for w in re.sub(r"\s+", " ", head_chunk).split() if w]
    rm = re.compile("|".join(p for _, p in _SPATIAL) + "|" + "|".join(rf"\b{k}\b" for k in _ORDINALS))
    keep = lambda w: not rm.fullmatch(w) and not _DROP.fullmatch(w) and not w.isdigit()  # noqa: E731
    for i, w in enumerate(words[:-1]):  # participle clause: "saw cutting the block" -> "saw"
        if (i and re.fullmatch(r"[a-z]{3,}ing", w) and _DET.fullmatch(words[i + 1])
                and any(keep(x) and not color_word(x) for x in words[:i])):
            words = words[:i]
            break
    words = [w for w in words if keep(w)]
    colors = [c for c in map(color_word, words) if c]
    if not colors:  # "woman in yellow", "man in a red shirt"
        m = re.search(r"\bin (?:a |an |the )?(" + "|".join(COLORS) + r")\b", base)
        colors = [COLORS[m.group(1)]] if m else []
    nouns = [w for w in words if not color_word(w)]
    of = " ".join(words).split(" of ")[0].split()
    head = next((w for w in reversed([w for w in of if not color_word(w)]) if w), nouns[-1] if nouns else "")
    if len(head) > 3 and head.endswith("s") and not head.endswith(("ss", "us")):
        head = head[:-1]  # "signs" also matches a "sign" label
    query = " ".join(words) or base.strip() or full
    return Hints(query=query, head=head, colors=list(dict.fromkeys(colors)), spatial=spatial, ordinal=ordinal)


def color_fraction(image: np.ndarray, box, colors: list[str], inner: float = 0.6) -> float:
    """Mean over `colors` of the share of pixels of that colour in the central `inner` part of `box`
    (RGB uint8 image). HSV rules: black V < .25; white S < .2, V > .7; gray S < .2; hues for the rest."""
    H, W = image.shape[:2]
    x0, y0, x1, y1 = (float(v) for v in box)
    mx, my = (x1 - x0) * (1 - inner) / 2, (y1 - y0) * (1 - inner) / 2
    xa, xb = int(np.clip(round(x0 + mx), 0, W - 1)), int(np.clip(round(x1 - mx), 1, W))
    ya, yb = int(np.clip(round(y0 + my), 0, H - 1)), int(np.clip(round(y1 - my), 1, H))
    crop = image[ya:max(yb, ya + 1), xa:max(xb, xa + 1)]
    if not crop.size or not colors:
        return 0.0
    hsv = cv2.cvtColor(np.ascontiguousarray(crop, np.uint8), cv2.COLOR_RGB2HSV).reshape(-1, 3).astype(float)
    h, s, v = hsv[:, 0] * 2.0, hsv[:, 1] / 255.0, hsv[:, 2] / 255.0
    chroma = (s >= 0.25) & (v >= 0.2)

    def hue(a, b):
        return chroma & (h >= a) & (h < b)

    rules = {"black": v < 0.25, "white": (s < 0.2) & (v > 0.7), "gray": (s < 0.2) & (v >= 0.25) & (v <= 0.75),
             "red": chroma & ((h < 15) | (h >= 340)), "orange": hue(15, 40) & (v >= 0.5),
             "brown": hue(10, 45) & (v < 0.6), "yellow": hue(40, 70), "green": hue(70, 165),
             "cyan": hue(165, 200), "blue": hue(195, 255), "purple": hue(255, 295),
             "pink": hue(295, 340) | (((h < 15) | (h >= 340)) & (s >= 0.12) & (s < 0.5) & (v > 0.7))}
    return float(np.mean([rules[c].mean() for c in colors if c in rules] or [0.0]))


def iou(a, b) -> float:
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua > 0 else 0.0


def nms(cands: list[dict], thr: float = NMS_IOU) -> list[dict]:
    """Greedy non-maximum suppression of [{"box", "score", ...}], highest score first."""
    keep: list[dict] = []
    for c in sorted(cands, key=lambda c: -c["score"]):
        if all(iou(c["box"], k["box"]) <= thr for k in keep):
            keep.append(c)
    return keep


def touches_border(box, image_size, margin: float = 1.0) -> bool:
    W, H = image_size
    return box[0] <= margin or box[1] <= margin or box[2] >= W - margin or box[3] >= H - margin


def _spatial_order(cands: list[dict], idx: list[int], words: list[str], image_size) -> list[int]:
    """`idx` sorted by the summed rank over spatial `words` (first = best match)."""
    W, H = image_size

    def key(c, w):
        x0, y0, x1, y1 = c["box"]
        cx, cy, area = (x0 + x1) / 2 / W, (y0 + y1) / 2 / H, (x1 - x0) * (y1 - y0) / (W * H)
        return {"left": cx, "right": -cx, "top": cy, "bottom": -cy, "center": math.hypot(cx - 0.5, cy - 0.5),
                "front": -y1 / H, "back": y1 / H, "large": -area, "small": area}[w]

    ranks = np.zeros(len(idx))
    for w in words:
        ranks += np.argsort(np.argsort([key(cands[i], w) for i in idx], kind="stable"), kind="stable")
    return [idx[j] for j in np.argsort(ranks, kind="stable")]


def choose_instance(cands: list[dict], hints: Hints, image_size, image: np.ndarray | None = None,
                    taken=(), rank: int | None = None, rel_keep: float = REL_KEEP) -> tuple[int | None, float, int]:
    """Pick the candidate (index into `cands`) a phrase means on one frame -> (index, quality, number
    of plausible candidates). `taken`: boxes of differently-described objects of the same kind;
    `rank`: instance r of a same-name pair, counted along the spatial words (default left to right)."""
    if not cands:
        return None, 0.0, 0
    idx = list(range(len(cands)))
    if hints.head and any(hints.head in str(c.get("label", "")) for c in cands):
        idx = [i for i in idx if hints.head in str(cands[i].get("label", ""))]
    adj = {i: float(cands[i]["score"]) for i in idx}
    if hints.colors and image is not None:
        for i in idx:
            adj[i] *= 0.15 + color_fraction(image, cands[i]["box"], hints.colors)
    for i in idx:
        if any(iou(cands[i]["box"], t) > 0.5 for t in taken):
            adj[i] *= 0.2
    top = max(adj.values())
    keep = [i for i in idx if adj[i] >= rel_keep * top]
    if rank is not None:
        group = sorted(keep, key=lambda i: -adj[i])[:max(2, rank + 1)]
        if len(group) <= rank:
            return None, 0.0, len(keep)
        group = _spatial_order(cands, group, hints.spatial or ["left"], image_size)
        return group[rank], min(adj[i] for i in group), len(keep)
    if hints.spatial or hints.ordinal is not None:
        order = _spatial_order(cands, keep, hints.spatial or ["left"], image_size)
        j = hints.ordinal or 0
        if j >= len(order):
            return None, 0.0, len(keep)
        return order[j], adj[order[j]], len(keep)
    best = max(keep, key=lambda i: adj[i])
    return best, adj[best], len(keep)


def pick_keyframe(dets: dict[int, list[dict]], hints: Hints, image_size, images: dict | None = None,
                  taken: dict | None = None, rank: int | None = None) -> tuple[int, int, float] | None:
    """(frame, candidate index, quality) of the frame where the phrase is best detected. When the
    choice is relational (spatial / ordinal / pair) only frames with the most candidates count fully;
    single instances touching the border are discounted."""
    res = {f: choose_instance(c, hints, image_size, (images or {}).get(f), (taken or {}).get(f, ()), rank)
           for f, c in sorted(dets.items())}
    n_max = max((n for _, _, n in res.values()), default=0)
    relational = bool(hints.spatial) or hints.ordinal is not None or rank is not None
    best = None
    for f, (i, q, n) in res.items():
        if i is None:
            continue
        if relational and n < n_max:
            q *= 0.5
        if rank is None and touches_border(dets[f][i]["box"], image_size):
            q *= 0.7
        if best is None or q > best[2] + 1e-12:
            best = (f, i, q)
    return best


# --------------------------------------------------------------------------- specs -> objects

def roles_for(spec: QuestionSpec) -> list[tuple[str, str, Quantity]]:
    """(role, object phrase, quantity) to track for one question; camera distances and generic
    names (gravity, camera) need no track."""
    out = []
    for role, q in (("prior", spec.prior), ("target", spec.target)):
        if q.kind == "camera_distance":
            continue
        names = [str(n) for n in (q.objects or []) if groundable(n)]
        if names:
            out.append((role, names[0], q))
        if len(names) > 1:
            out.append((role + "2", names[1], q))
    return out


def plan_objects(specs: dict[int, QuestionSpec]) -> tuple[dict[str, dict], dict[int, list[tuple[str, str, Quantity]]]]:
    """Distinct objects of one video ({key: {"phrase", "rank"}}) and each question's (role, key, quantity).
    A role and its "2" partner with the same phrase become instances 0 and 1 ("key#0", "key#1")."""
    objects: dict[str, dict] = {}
    roles: dict[int, list] = {}
    for qid, spec in specs.items():
        rs = [(role, name, q, *object_key(name)) for role, name, q in roles_for(spec)]
        keys = {r[0]: r[3] for r in rs}
        out = []
        for role, name, q, key, inst in rs:
            partner = role[:-1] if role.endswith("2") else role + "2"
            if inst is None and keys.get(partner) == key:
                inst = 1 if role.endswith("2") else 0
            k = f"{key}#{inst}" if inst is not None else key
            objects.setdefault(k, {"phrase": name, "rank": inst})
            out.append((role, k, q))
        roles[int(qid)] = out
    return objects, roles


def spec_times(specs) -> list[float]:
    ts = []
    for s in specs:
        for q in (s.target, s.prior):
            ts += [x for x in [q.time, *(q.window or [])] if isinstance(x, (int, float)) and math.isfinite(x)]
    return ts


def load_specs(path) -> dict[int, QuestionSpec]:
    """QuestionSpecs from a folder or file: run_open_vlm spec records ({"questions": {qid: {"spec"}}}),
    run_claude records ({"parsed": {"questions": [{"qid", "spec"}]}}), a list / dict of spec dicts,
    or JSONL. Unreadable entries are skipped."""
    p = Path(path)
    files = sorted([*p.glob("*.json"), *p.glob("*.jsonl")]) if p.is_dir() else [p]
    out: dict[int, QuestionSpec] = {}
    for f in files:
        try:
            text = f.read_text()
            lines = text.splitlines() if f.suffix == ".jsonl" else [text]
            items = [json.loads(x) for x in lines if x.strip()]
        except (OSError, ValueError):
            continue
        for it in items:
            _collect_specs(it, out)
    return out


def _collect_specs(obj, out: dict, qid=None) -> None:
    if isinstance(obj, list):
        for v in obj:
            _collect_specs(v, out, qid)
        return
    if not isinstance(obj, dict):
        return
    if isinstance(obj.get("parsed"), dict) and isinstance(obj.get("meta"), dict):  # a run_claude record:
        try:  # its specs as Track A uses them (prior value from the text, unit from the question, is_3d)
            out.update({q: a.spec for q, a in to_annotations(obj["parsed"], obj["meta"]).items()})
        except (KeyError, TypeError, ValueError):
            pass
        return
    if "target" in obj and "prior" in obj:
        q = obj.get("qid", qid)
        if q is not None:
            try:
                out[int(q)] = QuestionSpec.from_dict({**obj, "qid": int(q)})
            except (TypeError, KeyError, ValueError):
                pass
        return
    if isinstance(obj.get("spec"), dict):
        _collect_specs(obj["spec"], out, obj.get("qid", qid))
        return
    for k, v in obj.items():
        if k not in ("tracks", "raw", "raw_text", "meta", "usage", "objects"):
            _collect_specs(v, out, int(k) if str(k).isdigit() else qid)


# --------------------------------------------------------------------------- video

def read_video(path: str, max_frames: int = MAX_FRAMES) -> tuple[list[int], list[np.ndarray], int]:
    """(original frame indices, RGB frames, stride): every stride-th frame, stride = ceil(n / max_frames)."""
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise FileNotFoundError(path)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    stride = max(1, math.ceil(n / max_frames)) if max_frames and n > 0 else 1
    idx, frames, i = [], [], 0
    while cap.grab():
        if i % stride == 0:
            ok, img = cap.retrieve()
            if ok:
                idx.append(i)
                frames.append(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        i += 1
    cap.release()
    if not frames:
        raise RuntimeError(f"no frames decoded from {path}")
    return idx, frames, stride


def keyframe_positions(n: int, frame_idx: list[int], fps: float, times: list[float],
                       n_uniform: int = N_KEYFRAMES, max_total: int = 12) -> list[int]:
    """Positions (into the read frames) of uniform keyframes plus the frames nearest mentioned times."""
    pos = set(np.linspace(0, n - 1, min(n_uniform, n)).round().astype(int).tolist())
    arr = np.asarray(frame_idx, float) / fps
    for t in times:
        if len(pos) >= max_total:
            break
        if 0 <= t <= arr[-1] + 0.5:
            pos.add(int(np.argmin(np.abs(arr - t))))
    return sorted(pos)


# --------------------------------------------------------------------------- models (GPU, lazy)

def _device(device: str | None) -> str:
    if device:
        return device
    import torch
    return "cuda" if torch.cuda.is_available() else "cpu"


class Detector:
    """Text-prompted box detector: Grounding DINO ("gdino") or OWLv2 ("owlv2") via transformers.
    detect(images, query) -> per image [{"box": [x1, y1, x2, y2], "score", "label"}] (after NMS)."""

    def __init__(self, kind: str = "gdino", model_id: str | None = None, device: str | None = None,
                 threshold: float | None = None, text_threshold: float = 0.2, batch: int = 8):
        import torch
        if kind not in DETECTOR_MODELS:
            raise ValueError(f"unknown detector {kind!r} (expected {list(DETECTOR_MODELS)})")
        self.kind, self.model_id = kind, model_id or DETECTOR_MODELS[kind]
        self.name = kind
        self.device, self.batch = _device(device), batch
        self.threshold = DET_THRESHOLD[kind] if threshold is None else threshold
        self.text_threshold = text_threshold
        if kind == "gdino":
            from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor
            self.processor = AutoProcessor.from_pretrained(self.model_id)
            self.model = AutoModelForZeroShotObjectDetection.from_pretrained(self.model_id)
        else:
            from transformers import Owlv2ForObjectDetection, Owlv2Processor
            self.processor = Owlv2Processor.from_pretrained(self.model_id)
            self.model = Owlv2ForObjectDetection.from_pretrained(self.model_id)
        self.model = self.model.to(self.device).eval()
        self._torch = torch

    def _post(self, outputs, inputs, sizes):
        import inspect
        p = self.processor
        if self.kind == "gdino":
            fn = p.post_process_grounded_object_detection
            params = inspect.signature(fn).parameters
            kw = {"threshold" if "threshold" in params else "box_threshold": self.threshold,
                  "text_threshold": self.text_threshold, "target_sizes": sizes}
            return fn(outputs, inputs["input_ids"], **kw)
        # OWLv2 pads to a square: scaling by (S, S) is right for old and new post-processors
        sq = [(max(h, w), max(h, w)) for h, w in sizes]
        fn = getattr(p, "post_process_grounded_object_detection", None) or p.post_process_object_detection
        return fn(outputs=outputs, threshold=self.threshold, target_sizes=sq)

    def detect(self, images: list[np.ndarray], query: str) -> list[list[dict]]:
        from PIL import Image
        torch = self._torch
        out: list[list[dict]] = []
        for b in range(0, len(images), self.batch):
            chunk = images[b:b + self.batch]
            pils = [Image.fromarray(im) for im in chunk]
            sizes = [im.shape[:2] for im in chunk]
            if self.kind == "gdino":
                text = query.strip().lower().rstrip(".") + "."
                inputs = self.processor(images=pils, text=[text] * len(pils), return_tensors="pt")
            else:
                inputs = self.processor(text=[[f"a photo of a {query}"]] * len(pils), images=pils, return_tensors="pt")
            inputs = inputs.to(self.device)
            with torch.inference_mode():
                outputs = self.model(**inputs)
            for (h, w), r in zip(sizes, self._post(outputs, inputs, sizes)):
                labels = text_labels(r) if self.kind == "gdino" else []   # OWLv2: one query, labels are ids
                cands = []
                for j, (box, s) in enumerate(zip(r["boxes"].tolist(), r["scores"].tolist())):
                    x0, y0, x1, y1 = (float(np.clip(box[0], 0, w)), float(np.clip(box[1], 0, h)),
                                      float(np.clip(box[2], 0, w)), float(np.clip(box[3], 0, h)))
                    if x1 - x0 >= 2 and y1 - y0 >= 2:
                        lab = labels[j] if j < len(labels) else query
                        cands.append({"box": [round(v, 1) for v in (x0, y0, x1, y1)], "score": round(float(s), 4),
                                      "label": str(lab)})
                out.append(nms(cands))
        return out


def text_labels(result: dict) -> list[str]:
    """Per-box text labels of a post-processed detection result: "text_labels" (transformers >= 4.51)
    or "labels" when those are strings. Never truth-tests values: "labels" may be a tensor of class ids."""
    for k in ("text_labels", "labels"):
        v = result.get(k)
        if v is not None and not hasattr(v, "dtype") and all(isinstance(x, str) for x in v):
            return list(v)
    return []


def _mask_conf(logits) -> tuple[np.ndarray, float]:
    import torch
    m = logits > 0
    conf = float(torch.sigmoid(logits[m].float()).mean()) if bool(m.any()) else 0.0
    return m.cpu().numpy(), conf


class Segmenter:
    """SAM 2 video propagation. backend "official" (facebookresearch/sam2 package), "hf"
    (transformers Sam2VideoModel) or "auto" (official, else - not installed or failing to load - hf).
    propagate(frames, {obj_id: (frame_pos, box)}) yields (frame_pos, obj_id, bool mask, confidence)
    for every frame and object: forward from the object's prompt frame, backward before it."""

    def __init__(self, backend: str = "auto", model_id: str = SAM_MODEL, device: str | None = None):
        import torch
        self.device, self.model_id, self._torch = _device(device), model_id, torch
        cuda = self.device.startswith("cuda")
        self.dtype = torch.bfloat16 if cuda and torch.cuda.is_bf16_supported() else torch.float32
        if backend != "auto":
            self._load(backend)
            return
        try:
            self._load("official")
        except Exception as e:  # noqa: BLE001 - not installed, or its hydra config / checkpoint / CUDA setup failed
            print(f"official SAM 2 unavailable ({type(e).__name__}: {str(e)[:300]}); using transformers' Sam2Video")
            if cuda:
                torch.cuda.empty_cache()
            self._load("hf")

    def _load(self, backend: str) -> None:
        if backend == "official":
            from sam2.sam2_video_predictor import SAM2VideoPredictor
            self.predictor = SAM2VideoPredictor.from_pretrained(self.model_id, device=self.device)
        elif backend == "hf":
            from transformers import Sam2VideoModel, Sam2VideoProcessor
            self.model = Sam2VideoModel.from_pretrained(self.model_id, dtype=self.dtype).to(self.device).eval()
            self.processor = Sam2VideoProcessor.from_pretrained(self.model_id)
        else:
            raise ValueError(f"unknown SAM 2 backend {backend!r}")
        self.backend, self.name = backend, f"sam2-{backend}"

    def _autocast(self):
        import contextlib
        torch = self._torch
        if self.device.startswith("cuda") and self.dtype == torch.bfloat16:
            return torch.autocast("cuda", dtype=torch.bfloat16)
        return contextlib.nullcontext()

    def propagate(self, frames: list[np.ndarray], prompts: dict[int, tuple[int, list[float]]]):
        if not prompts:
            return
        yield from (self._official if self.backend == "official" else self._hf)(frames, prompts)

    def _official(self, frames, prompts):
        import shutil
        import tempfile
        torch, pred = self._torch, self.predictor
        tmp = tempfile.mkdtemp(prefix="sam2_frames_")
        try:
            for i, im in enumerate(frames):  # the predictor reads a folder of <index>.jpg
                cv2.imwrite(f"{tmp}/{i:05d}.jpg", cv2.cvtColor(im, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 95])
            with torch.inference_mode(), self._autocast():
                state = pred.init_state(video_path=tmp, offload_video_to_cpu=True)
                for oid, (k, box) in prompts.items():
                    pred.add_new_points_or_box(state, frame_idx=int(k), obj_id=int(oid),
                                               box=np.asarray(box, np.float32))
                ks = [int(k) for k, _ in prompts.values()]
                for f, ids, logits in pred.propagate_in_video(state, start_frame_idx=min(ks)):
                    for i, oid in enumerate(ids):
                        if f >= prompts[oid][0]:
                            yield (f, oid, *_mask_conf(logits[i, 0]))
                if max(ks) > 0:
                    for f, ids, logits in pred.propagate_in_video(state, start_frame_idx=max(ks), reverse=True):
                        for i, oid in enumerate(ids):
                            if f < prompts[oid][0]:
                                yield (f, oid, *_mask_conf(logits[i, 0]))
                pred.reset_state(state)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    def _hf(self, frames, prompts):
        torch = self._torch
        H, W = frames[0].shape[:2]
        with torch.inference_mode(), self._autocast():
            session = self.processor.init_video_session(video=np.stack(frames), inference_device=self.device,
                                                        video_storage_device="cpu", dtype=self.dtype)
            for oid, (k, box) in prompts.items():  # one object at a time: prompts sit on different frames
                session.reset_tracking_data()
                self.processor.add_inputs_to_inference_session(
                    inference_session=session, frame_idx=int(k), obj_ids=int(oid),
                    input_boxes=[[[float(v) for v in box]]])
                for reverse in (False, True):
                    if reverse and k == 0:
                        continue
                    for out in self.model.propagate_in_video_iterator(session, start_frame_idx=int(k), reverse=reverse):
                        if reverse and out.frame_idx == k:
                            continue
                        masks = self.processor.post_process_masks([out.pred_masks], original_sizes=[[H, W]],
                                                                  binarize=False)[0]
                        yield (int(out.frame_idx), oid, *_mask_conf(masks[0, 0]))
        del session
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


# --------------------------------------------------------------------------- per-video tracking

def _size_like(q: Quantity, role: str) -> bool:
    return q.kind in ("size", "other") or (q.kind == "distance" and not role.endswith("2") and len(q.objects or []) < 2)


class ModelLoadError(RuntimeError):
    """The detector or SAM 2 could not be built; every further video would fail the same way."""


class CVTracker:
    """Detector + SAM 2 over the videos of a split. `detector` / `segmenter` may be names (models load
    on first use; a load failure is remembered and raised as ModelLoadError) or objects with the same
    detect() / propagate() interface (tests)."""

    def __init__(self, detector="gdino", segmenter="auto", det_model: str | None = None,
                 sam_model: str = SAM_MODEL, device: str | None = None, max_frames: int = MAX_FRAMES,
                 n_keyframes: int = N_KEYFRAMES, point_mode: str = "centroid", det_threshold: float | None = None):
        self._det_cfg = (detector, det_model, det_threshold)
        self._seg_cfg = (segmenter, sam_model)
        self._det = None if isinstance(detector, str) else detector
        self._seg = None if isinstance(segmenter, str) else segmenter
        self._load_errors: dict[str, str] = {}
        self.device, self.max_frames, self.n_keyframes, self.point_mode = device, max_frames, n_keyframes, point_mode

    def _model(self, attr: str, build):
        if getattr(self, attr) is None:
            what = "detector" if attr == "_det" else "SAM 2"
            if attr in self._load_errors:
                raise ModelLoadError(f"{what} failed to load earlier: {self._load_errors[attr]}")
            try:
                setattr(self, attr, build())
            except Exception as e:  # noqa: BLE001 - remembered so later videos fail fast
                self._load_errors[attr] = f"{type(e).__name__}: {str(e)[:500]}"
                raise ModelLoadError(f"{what} failed to load: {self._load_errors[attr]}") from e
        return getattr(self, attr)

    @property
    def det(self):
        kind, model_id, thr = self._det_cfg
        return self._model("_det", lambda: Detector(kind, model_id, self.device, threshold=thr))

    @property
    def seg(self):
        backend, model_id = self._seg_cfg
        return self._model("_seg", lambda: Segmenter(backend, model_id, self.device))

    @property
    def det_name(self) -> str:
        return self._det_cfg[0] if isinstance(self._det_cfg[0], str) else getattr(self._det, "name", "detector")

    @property
    def seg_name(self) -> str:
        if isinstance(self._seg_cfg[0], str) and self._seg_cfg[0] != "auto":
            return f"sam2-{self._seg_cfg[0]}"
        return getattr(self._seg, "name", "sam2") if self._seg is not None else "sam2"

    @property
    def source(self) -> str:
        return f"{self.det_name}+sam2"

    def _cache_ok(self, cache: dict | None) -> bool:
        m = (cache or {}).get("meta", {})
        return (m.get("version") == CACHE_VERSION and m.get("detector") == self.det_name
                and m.get("max_frames") == self.max_frames)

    def track_video(self, rows, specs: dict[int, QuestionSpec], cache: dict | None = None) -> tuple[dict, dict]:
        """Record {"video_id", "model", "meta", "objects", "tracks": {qid: [RoleTrack dicts]}, "flags"}
        for the questions in `rows` (one video, qp.data columns) that have a spec, and the updated cache."""
        first = rows.iloc[0]
        vid, path = str(first.video_id), str(first.video_path)
        fps = video_fps(first.fps, path)[0]   # dataset fps; the container's if missing (as Track A)
        qspecs = {int(q): specs[int(q)] for q in rows.qid if int(q) in specs}
        objects, roles = plan_objects(qspecs)
        if not self._cache_ok(cache):
            cache = {"meta": {"version": CACHE_VERSION, "detector": self.det_name, "max_frames": self.max_frames},
                     "dets": {}, "objects": {}}
        need = [k for k in objects if k not in cache["objects"]]
        if need or "image_size" not in cache["meta"]:
            self._run(path, fps, objects, need, list(qspecs.values()), cache)
        rec = self._record(vid, fps, objects, roles, cache)
        return rec, cache

    def _run(self, path: str, fps: float, objects: dict, need: list[str], specs: list, cache: dict) -> None:
        if need:
            _ = self.det, self.seg   # load (or fail) before decoding the video
        frame_idx, frames, stride = read_video(path, self.max_frames)
        H, W = frames[0].shape[:2]
        size = (W, H)
        cache["meta"].update(image_size=[W, H], stride=stride, n_frames=len(frames), segmenter=self.seg_name)
        if not need:
            return
        kpos = keyframe_positions(len(frames), frame_idx, fps, spec_times(specs), self.n_keyframes)
        images = {frame_idx[p]: frames[p] for p in kpos}
        hints = {k: parse_phrase(objects[k]["phrase"]) for k in objects}
        dets = {}
        for q in dict.fromkeys(hints[k].query for k in need):
            if q not in cache["dets"]:
                found = self.det.detect([images[f] for f in sorted(images)], q)
                cache["dets"][q] = {str(f): c for f, c in zip(sorted(images), found)}
            dets[q] = {int(f): c for f, c in cache["dets"][q].items()}
        def taken_for(key: str) -> dict[int, list]:
            """{keyframe: [boxes]} of the objects told apart from `key` that already have a keyframe
            (this run or a cached one). Only keyframe boxes, not their masks on other frames, so an
            object's choice is the same whether the others come from the cache or not."""
            out: dict[int, list] = {}
            for k2, h2 in hints.items():
                o = cache["objects"].get(k2) or {}
                if k2 != key and "box" in o and hints[key].distinct_from(h2):
                    out.setdefault(int(o["keyframe"]), []).append(o["box"])
            return out

        prompts, ids = {}, {}
        for n, key in enumerate(need, 1):
            h, d = hints[key], dets[hints[key].query]
            pick = pick_keyframe(d, h, size, images, taken_for(key), objects[key]["rank"])
            entry = {"phrase": objects[key]["phrase"], "query": h.query, "rank": objects[key]["rank"],
                     "frames": {}, "flags": []}
            if pick is None:
                entry["flags"].append("not_detected")
                cache["objects"][key] = entry
                continue
            f, i, quality = pick
            c = d[f][i]
            entry.update(keyframe=f, keyframe_t=round(f / fps, 4), box=c["box"], det_score=c["score"],
                         quality=round(quality, 4))
            cache["objects"][key] = entry
            prompts[n] = (frame_idx.index(f), c["box"])
            ids[n] = key
        for p, oid, mask, conf in (self.seg.propagate(frames, prompts) if prompts else ()):
            feat = mask_features(mask)
            if feat is not None:
                feat["conf"] = round(conf, 3)
                cache["objects"][ids[oid]]["frames"][str(frame_idx[p])] = feat
        if prompts:
            cache["meta"]["segmenter"] = self.seg_name
        for key in ids.values():  # agreement of the SAM 2 track with the detector on keyframes
            o, h, taken = cache["objects"][key], hints[key], taken_for(key)
            hits = []
            for f, cands in dets[h.query].items():
                feat = o["frames"].get(str(f))
                i, _, _ = choose_instance(cands, h, size, images.get(f), taken.get(f, ()), o["rank"])
                if feat and i is not None:
                    hits.append(iou(feat["box"], cands[i]["box"]) > 0.5)
            o["agree"] = round(float(np.mean(hits)), 3) if hits else None
            if not o["frames"]:
                o["flags"].append("empty_track")
            elif len(hits) >= 3 and np.mean(hits) < 0.5:
                o["flags"].append("low_detector_agreement")

    def _record(self, vid: str, fps: float, objects: dict, roles: dict, cache: dict) -> dict:
        tracks, flags = {}, {}
        for qid, rs in roles.items():
            out, fl = [], []
            for role, key, q in rs:
                o = cache["objects"].get(key, {})
                mode = dimension_mode(q.dimension, o.get("phrase", "")) if _size_like(q, role) else None
                if mode is None and _size_like(q, role):   # a ruler's calibre: no track, or geometry
                    fl.append(f"{role}:unmeasurable_dimension")   # would scale by the whole box
                    continue
                obs = build_obs(o.get("frames", {}), fps, mode, o.get("phrase", ""), self.point_mode,
                                o.get("det_score", 1.0))
                fl += [f"{role}:{x}" for x in o.get("flags", [])]
                if obs:
                    out.append(RoleTrack(role=role, object=o["phrase"], obs=obs, source=self.source).to_dict())
                elif not o.get("flags"):
                    fl.append(f"{role}:no_obs")
            tracks[str(qid)], flags[str(qid)] = out, sorted(set(fl))
        objs = {k: {x: v for x, v in o.items() if x != "frames"} | {"n_frames": len(o.get("frames", {}))}
                for k, o in cache["objects"].items() if k in objects}
        meta = {k: cache["meta"].get(k) for k in ("image_size", "stride", "n_frames", "detector", "segmenter")}
        return {"video_id": vid, "model": self.source, "meta": {**meta, "fps": fps, "point_mode": self.point_mode},
                "objects": objs, "tracks": tracks, "flags": flags}
