"""Dense CPU tracking: an annotator's sparse pixel annotations -> per-frame measurements (no API cost).

Claude annotates 1-44 frames per video and every annotated point carries a few pixels of noise;
the geometry solver fits positions over time. This module turns a sparse RoleTrack into a dense one
(source "dense") from the video itself. Coordinates are always ORIGINAL video pixels.

Motion (`dense_motion`). Anchors = the annotated frames: the box, else the point with a box size from
the track's nearest box, the same object's boxes in other tracks (only those centred on this track's
point at their time: borrowed_sizes), its extents, or the scale of the image blob under the point
(Laplacian of Gaussian); a track with no size at all is left alone ("no_size": a template of the
wrong size locks onto background). Every segment between consecutive anchors is tracked twice,
forward from its first anchor and backward from its second, by NCC template matching on frames
scaled so the template is <= TEMPLATE_MAX px. Template pixels are weighted to the object
(template_weight: GrabCut in the box, convex hull plus a MASK_RING px ring; else the inscribed
ellipse): the box's background is static while the object moves, and unweighted it drags every
match towards zero motion - most for loose boxes and slow objects on textured backgrounds. A
segment the weighted templates lose is retried with whole boxes. The template follows the object
frame to frame and is pulled back onto the anchor's own template, searched at three scales,
whenever that still matches (drift correction, Matthews et al. 2004; the scale search keeps the
tracked point the same point of a growing or shrinking object). Weak frame-to-frame matches are
occlusions (no point, template kept, constant-velocity coasting). The search covers the motion
prediction and the annotator's interpolated track. Forward-backward check per segment: the two
passes differ by their templates' reference offset d, which must stay constant (spread <= FB_TOL) and
small (|d| <= D_TOL x template, or 4.5 annotator sd: else they followed different things); the fused
path blends both passes, each weighted near its own anchor. A failing segment is retried once
across its far anchor (an annotator outlier), else left as a gap. The chained d's give the path of
each piece in one reference; a bias common to every link (a lagging template) is invisible to the
forward-backward check but scales the path, so the chain's scale along the motion is compared with
the annotator's points (chain_scale; standard error from the annotator's prior noise): rejected
("scale") when it spans less than they do (lag) or runs against them, beyond SCALE_Z sd of the
difference; else combined with the annotator's estimate (prior sd SCALE_SIG of the chain's scale).
The anchors' offsets to the annotator's reference are then solved by least squares (_fuse_offsets:
smooth along the chain vs the annotator's points, noisy, Huber-weighted), so the annotator's
per-frame noise is not copied into the path and the path keeps the annotator's reference point
(centres for distances). Accepted when the good segments cover >=
MIN_COVER of the anchors' span and the annotator's points agree with the path: median residual <=
RESID_TOL x ANCHOR_SIG px of the image the annotator saw (not scaled by the object's size: drift
onto a neighbouring object stays well within a big object's size), >= RESID_INSIDE of them within
twice that; anchors in gaps keep the annotator's point. Output: one point per tracked frame plus the
original obs without points (boxes, extents kept), as qp.refine does.

Size (`dense_size`), opt-in. On every annotated frame with a box the extent is re-measured in the
full-resolution frame: GrabCut seeded by the box (dimension by qp.open.cv_track.dimension_mode /
extent_from_features; boundary refined to sub-pixel: alpha-weighted area for round objects, colour
edge snapping for other extents), or (SIZE_METHOD "snap") only snapping the annotator's endpoints
to the colour edge along their line. A frame keeps the annotator's extent when the segmentation is
unreliable (mask fill, mask filling its seed rect, ratio to the annotator's extent outside SIZE_RATIO).

    densify_annotations(anns, {qid: video_path}, {qid: (fps, (W, H), seen_scale)}, what="motion",
                        cache_dir=..., workers=4)

Frames are decoded once per video (sequentially, exact for any codec) and downscaled to <= WORK_SIDE
for tracking; size crops come from the full-resolution frames. Results are cached per video and
object (JSON keyed by the annotations, the borrowed sizes, the annotator's image scale and the
settings the result depends on; safe to share between concurrent runs).
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import math
import os
import tempfile
import warnings
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

from .spec import Obs, RoleTrack

VERSION = 4
MOTION = ("speed", "acceleration", "displacement", "path_length")
WORK_SIDE = 1280          # long edge of the frames tracked on (larger videos are downscaled)
WORK_BYTES = 6e8          # the decoded window is downscaled further to stay under this
TEMPLATE_MAX = 48         # px: an object's frames are scaled so its template's long side is at most this
TEMPLATE_MIN = 7          # px: smallest template side
TEMPLATE_MASK = "grabcut" # template pixel weights: "grabcut" (the object in the box), "ellipse" (inscribed), "none"
MASK_RING = 1.0           # px (template scale): the object's mask is grown by this ring (its outline) ...
MASK_FILL = (0.1, 0.92)   # ... and used when its area / the box area lies inside this (else: the inscribed ellipse)
NCC_LOST = 0.5            # frame-to-frame NCC below this: occluded / lost frame
NCC_ANCHOR = 0.75         # the anchor template must match this well to pull the track back (drift correction)
MAX_COAST = 8             # consecutive lost frames before a pass gives up
FB_TOL = 0.12             # max spread of the forward-backward offset, x template long side (object px) ...
FB_TOL_MIN = 1.5          # ... and at least this many object px
MIN_COVER = 0.6           # share of the anchors' span the good segments must cover
LINK_SIG = 0.005          # sd of one chained template offset, x template long side (object px) ...
LINK_SIG_MIN = 0.1        # ... at least this many object px (or half the segment's forward-backward spread)
ANCHOR_SIG = 2.0          # sd of an annotator's point in the pixels it saw ...
ANCHOR_SIG_SIZE = 0.05    # ... or this share of the object's size, if larger
RESID_TOL = 3.0           # median |annotator point - dense path| <= this x ANCHOR_SIG px of the image the
                          # annotator saw (not scaled by the object's size: drift onto a neighbour stays
                          # within a big object's size)
RESID_INSIDE = 0.8        # share of the annotator's points that must lie within 2 x that tolerance
SCALE_SIG = 0.01          # prior sd of the chained path's scale along the motion (vs the annotator's points) ...
SCALE_Z = 3.0             # ... a chain shorter than the annotator's by more than this many sd of the difference
                          # (or running against it) is rejected
D_TOL = 0.25              # max offset between two anchors' template references, x template side ...
                          # (or 4.5 annotator sd): larger, the two passes followed different things
SIZE_METHOD = "grabcut"   # "grabcut" | "snap"
SIZE_RATIO = (0.75, 1.33) # a re-measured extent outside this ratio of the annotator's is implausible
SIZE_MARGIN = 0.25        # GrabCut crop margin around the box (share of the box side)
SIZE_RECT_PAD = 0.08      # GrabCut seed rect = box padded by this share (a tight box would cut the object)
SIZE_FILL = (0.2, 0.97)   # mask area / seed rect area outside this: segmentation unreliable
SIZE_MAX_SIDE = 400       # crops are segmented at most this large (long side)
SIZE_SNAP = 2.5           # px (segmented crop): a mask extent's endpoints snap to the colour edge within this


# --------------------------------------------------------------------------- video


@dataclass
class Window:
    """Frames [f0, f1] of a video at working resolution (uint8 BGR) plus full-resolution crops."""
    path: str
    size: tuple[int, int]                 # original (W, H)
    work: dict[int, np.ndarray] = field(default_factory=dict)
    crops: dict[tuple, np.ndarray] = field(default_factory=dict)   # (frame, x0, y0, x1, y1) -> crop

    @property
    def work_size(self) -> tuple[int, int]:
        img = next(iter(self.work.values()))
        return img.shape[1], img.shape[0]


def decode(path: str, frames: set[int], crops: dict[int, list[tuple[int, int, int, int]]] | None = None,
           work_side: int = WORK_SIDE, max_bytes: float = WORK_BYTES) -> Window:
    """One sequential pass: `frames` at working resolution, `crops` ({frame: [(x0, y0, x1, y1)]} in
    original pixels, clipped to the image) at full resolution."""
    crops = crops or {}
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise FileNotFoundError(path)
    W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    s = min(1.0, work_side / max(W, H, 1))
    if frames:
        s = min(s, math.sqrt(max_bytes / (3.0 * W * H * len(frames))))
    wsize = (max(1, round(W * s)), max(1, round(H * s)))
    win = Window(path, (W, H))
    last = max([*frames, *crops], default=-1)
    i = 0
    try:
        while i <= last and cap.grab():
            if i in frames or i in crops:
                ok, img = cap.retrieve()
                if not ok:
                    break
                if i in frames:
                    win.work[i] = img if wsize == (W, H) else cv2.resize(img, wsize, interpolation=cv2.INTER_AREA)
                for (x0, y0, x1, y1) in crops.get(i, []):
                    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
                    if x1 > x0 and y1 > y0:
                        win.crops[(i, x0, y0, x1, y1)] = img[y0:y1, x0:x1].copy()
            i += 1
    finally:
        cap.release()
    return win


# --------------------------------------------------------------------------- matching


def _peak_offset(a: float, b: float, c: float) -> float:
    d = a - 2 * b + c
    return float(np.clip(0.5 * (a - c) / d, -0.5, 0.5)) if d < 0 else 0.0


def match(img: np.ndarray, templ: np.ndarray, centres, radius: float, weight: np.ndarray | None = None
          ) -> tuple[np.ndarray | None, float]:
    """Best TM_CCOEFF_NORMED match of `templ` (pixels weighted by `weight`, float32 of the template's
    size, if given) whose centre lies within `radius` of any of `centres` (OpenCV pixel coordinates:
    pixel (i, j) centred at (j, i)) -> (sub-pixel centre, peak), or (None, -1) when the search region
    does not fit in the image."""
    th, tw = templ.shape[:2]
    hx, hy = (tw - 1) / 2, (th - 1) / 2
    cs = np.atleast_2d(np.asarray(centres, float))
    x0 = int(math.floor(cs[:, 0].min() - radius - hx))
    y0 = int(math.floor(cs[:, 1].min() - radius - hy))
    x1 = int(math.ceil(cs[:, 0].max() + radius + hx)) + 1
    y1 = int(math.ceil(cs[:, 1].max() + radius + hy)) + 1
    H, W = img.shape[:2]
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if x1 - x0 < tw + 2 or y1 - y0 < th + 2:
        return None, -1.0
    if weight is None:
        res = cv2.matchTemplate(img[y0:y1, x0:x1], templ, cv2.TM_CCOEFF_NORMED)
    else:
        res = cv2.matchTemplate(img[y0:y1, x0:x1], templ, cv2.TM_CCOEFF_NORMED, mask=weight)
    res = np.nan_to_num(res, nan=-1.0, posinf=-1.0, neginf=-1.0)
    _, peak, _, (j, i) = cv2.minMaxLoc(res)
    dx = _peak_offset(res[i, j - 1], res[i, j], res[i, j + 1]) if 0 < j < res.shape[1] - 1 else 0.0
    dy = _peak_offset(res[i - 1, j], res[i, j], res[i + 1, j]) if 0 < i < res.shape[0] - 1 else 0.0
    return np.array([x0 + j + dx + hx, y0 + i + dy + hy]), float(peak)


def _patch(img: np.ndarray, centre, tsize: tuple[int, int]) -> np.ndarray:
    return cv2.getRectSubPix(img, tsize, (float(centre[0]), float(centre[1])))


def _scaled_patch(img: np.ndarray, centre, tsize: tuple[int, int], scale: float,
                  border: int = cv2.BORDER_REPLICATE) -> np.ndarray:
    """Patch of size tsize showing img around `centre` magnified `scale` times (exact, centred)."""
    w, h = tsize
    k = 1.0 / scale
    M = np.array([[k, 0, centre[0] - k * (w - 1) / 2], [0, k, centre[1] - k * (h - 1) / 2]], np.float64)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=border)


def _scaled_weight(weight: np.ndarray | None, tsize: tuple[int, int], scale: float) -> np.ndarray | None:
    """The anchor template's weights for a template of size tsize at `scale` x the anchor's (as
    _scaled_patch of the anchor frame around the template centre; zero outside the anchor template),
    or None (all pixels) when the weights cover too little of it."""
    if weight is None:
        return None
    h, w = weight.shape
    out = _scaled_patch(weight, ((w - 1) / 2, (h - 1) / 2), tsize, scale, cv2.BORDER_CONSTANT)
    return out if float(out.sum()) >= 9.0 else None


def _ellipse_weight(tsize: tuple[int, int], grow: float = 0.0) -> np.ndarray:
    w, h = tsize
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ax, ay = w / 2 + grow, h / 2 + grow
    return ((((xx - (w - 1) / 2) / ax) ** 2 + ((yy - (h - 1) / 2) / ay) ** 2) <= 1.0).astype(np.float32)


def template_weight(img: np.ndarray, centre, tsize: tuple[int, int], how: str | None = None
                    ) -> tuple[np.ndarray | None, str]:
    """Weights (float32 0/1, tsize) of an anchor template's pixels and how they were found: the
    object segmented by GrabCut inside the template rect (the annotator's box), its component at
    (or nearest) the centre, grown by a MASK_RING px ring so the object's outline - a flat object's
    only position information - stays in; the inscribed ellipse when the segmentation is
    implausible. The box's background is static while the object moves: unweighted it pulls every
    match towards zero motion, the more the looser the box and the slower the object (so does the
    ring, hence a thin one)."""
    how = how or TEMPLATE_MASK
    if how == "none":
        return None, "none"
    w, h = tsize
    grow = MASK_RING
    ellipse = _ellipse_weight(tsize, grow)
    if how != "grabcut" or min(w, h) < 9:
        return ellipse, "ellipse"
    m = int(math.ceil(max(6.0, 0.35 * max(w, h))))
    crop = cv2.getRectSubPix(img, (w + 2 * m, h + 2 * m), (float(centre[0]), float(centre[1])))
    mask = np.zeros(crop.shape[:2], np.uint8)
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    try:
        cv2.setRNGSeed(12345)   # GrabCut's k-means initialisation draws from OpenCV's global RNG
        cv2.grabCut(crop, mask, (m, m, w, h), bgd, fgd, 4, cv2.GC_INIT_WITH_RECT)
    except cv2.error:
        return ellipse, "ellipse"
    fg = ((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD))[m:m + h, m:m + w].astype(np.uint8)
    n, lab, stats, cents = cv2.connectedComponentsWithStats(fg, connectivity=8)
    if n < 2:
        return ellipse, "ellipse"
    c = np.array([(w - 1) / 2, (h - 1) / 2])
    k = lab[int(round(c[1])), int(round(c[0]))]
    if k == 0:   # the centre is background: the largest component near it
        k = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA] / (1.0 + np.linalg.norm(cents[1:] - c, axis=1)
                                                               / max(w, h))))
    # its convex hull: a multicoloured object (a football's black patches, a car's windows) is split
    # by GrabCut's colour models, and a template of one colour's pattern loses a rotating object
    hull = cv2.convexHull(cv2.findNonZero((lab == k).astype(np.uint8)))
    obj = np.zeros((h, w), np.uint8)
    cv2.fillConvexPoly(obj, hull, 1)
    fill = float(obj.sum()) / float(w * h)
    if not MASK_FILL[0] <= fill <= MASK_FILL[1]:
        return ellipse, "ellipse"
    g = max(1, int(round(grow)))
    return cv2.dilate(obj, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * g + 1, 2 * g + 1))).astype(np.float32), \
        "grabcut"


SCALE_STEP = 1.04         # scale search ladder of the anchor template (per frame: s / step, s, s * step)


def track_pass(imgs: dict[int, np.ndarray], f_a: int, f_b: int, c_a, tsize: tuple[int, int],
               guide=None, weight: np.ndarray | None = None) -> dict[int, tuple[np.ndarray, float, float]]:
    """One direction from anchor frame f_a (template of size tsize centred at c_a) to f_b inclusive.
    Returns {frame: (centre, ncc, scale vs the anchor)}; lost (occluded) frames are absent.
    guide(frame) -> a coarse position (the annotator's interpolated track) searched as well as the
    motion prediction. The anchor template is matched at three scales around the current one, so
    the tracked point stays the same point of an object that grows or shrinks. weight: the anchor
    template's pixel weights (template_weight), carried (scaled) to every template of the pass."""
    step = 1 if f_b >= f_a else -1
    tw, th = tsize
    img_a = imgs[f_a]
    T = _patch(img_a, c_a, tsize)
    wT = weight
    p, v, s = np.asarray(c_a, float), np.zeros(2), 1.0
    p_last, f_last = p.copy(), f_a
    out = {f_a: (p.copy(), 1.0, 1.0)}
    lost = 0
    ls = math.log(SCALE_STEP)
    for f in range(f_a + step, f_b + step, step):
        img = imgs.get(f)
        if img is None:
            break
        size = max(tw, th) * s
        pred = p + v
        radius = max(0.5 * size, 2.0 * float(np.linalg.norm(v)), 4.0) * (1 + 0.5 * lost)
        centres = [pred] + ([guide(f)] if guide is not None else [])
        p1, n1 = match(img, T, centres, radius, wT)
        if p1 is None or n1 < NCC_LOST:   # occluded or lost: coast, keep the template
            lost += 1
            if lost > MAX_COAST:
                break
            p = pred
            continue
        cur = (_odd(tw * s), _odd(th * s))
        fits = []
        for q in (-1, 0, 1):   # drift correction: the anchor's own template, at three scales
            sq = s * math.exp(q * ls)
            Tq = _scaled_patch(img_a, c_a, cur, sq)
            p2, n2 = match(img, Tq, [p1], max(2.0, 0.15 * size), _scaled_weight(weight, cur, sq))
            fits.append((n2, p2))
        best = max(range(3), key=lambda j: fits[j][0])
        if fits[best][1] is not None and fits[best][0] >= NCC_ANCHOR and \
                np.linalg.norm(fits[best][1] - p1) <= max(1.5, 0.1 * size):
            dq = _peak_offset(*(x[0] for x in fits)) if best == 1 else (best - 1) * 0.5
            p1 = fits[best][1]
            s = float(np.clip(s * math.exp(dq * ls), 0.5, 2.0))
        v = (p1 - p_last) / abs(f - f_last)
        p, p_last, f_last, lost = p1, p1.copy(), f, 0
        cur = (_odd(tw * s), _odd(th * s))
        T = _patch(img, p, cur)
        wT = _scaled_weight(weight, cur, s)
        out[f] = (p.copy(), n1, s)
    return out


# --------------------------------------------------------------------------- motion


@dataclass
class Anchor:
    frame: int
    centre: np.ndarray        # template centre, original px (box centre, else the point)
    ref: np.ndarray           # the annotator's reference point, original px (point, else box centre)
    wh: tuple[float, float]   # box size, original px
    boxed: bool


def _odd(x: float) -> int:
    n = max(TEMPLATE_MIN, int(round(x)))
    return n if n % 2 else n + 1


def anchors_from_obs(obs: list[Obs], fps: float, size_hint=None, size_probe=None) -> tuple[list[Anchor], list[str]]:
    """Anchors (one per annotated frame with a point or box, sorted) and notes on how sizes were found:
    the anchor's box, else the track's nearest box, size_hint(frame) -> (w, h) (the object's boxes
    in its other tracks), the track's extents, size_probe(frame, point) -> side (blob scale in the
    image), else none ("no_size", size 0)."""
    notes: list[str] = []
    rows = {}
    for o in obs:
        if o.point is None and o.box is None:
            continue
        f = int(round(o.t * fps))
        rows.setdefault(f, o)
    boxed = {f: o.box for f, o in rows.items() if o.box is not None and o.box[2] > o.box[0] and o.box[3] > o.box[1]}
    ext = [math.hypot(o.extent[1][0] - o.extent[0][0], o.extent[1][1] - o.extent[0][1])
           for o in obs if o.extent is not None]
    out = []
    for f in sorted(rows):
        o = rows[f]
        b = boxed.get(f)
        if b is not None:
            wh, how = (b[2] - b[0], b[3] - b[1]), None
        elif boxed:
            g = min(boxed, key=lambda k: (abs(k - f), k))
            wh, how = (boxed[g][2] - boxed[g][0], boxed[g][3] - boxed[g][1]), "size_from_track_box"
        elif size_hint is not None and (h := size_hint(f)) is not None:
            wh, how = h, "size_from_other_track"
        elif ext and np.median(ext) > 2:
            s = float(np.median(ext))
            wh, how = (s, s), "size_from_extent"
        elif size_probe is not None and o.point is not None and (s := size_probe(f, o.point)):
            wh, how = (s, s), "size_from_blob"
        else:
            wh, how = (0.0, 0.0), "no_size"
        if how and how not in notes:
            notes.append(how)
        centre = np.array([(b[0] + b[2]) / 2, (b[1] + b[3]) / 2]) if b is not None else np.asarray(o.point, float)
        ref = np.asarray(o.point, float) if o.point is not None else centre
        out.append(Anchor(f, centre, ref, (float(wh[0]), float(wh[1])), b is not None))
    return out, notes


def blob_size(grey: np.ndarray, point, max_side: float) -> float | None:
    """Diameter (px) of the blob at `point` (pixel-centre coordinates): 2 sqrt(2) sigma at the
    strongest scale-normalised Laplacian-of-Gaussian response over sigma; None without an interior
    peak or with a weak response (< 4 grey levels)."""
    sigmas = np.geomspace(0.8, max(1.0, max_side / 2.83), 18)
    x, y = float(point[0]), float(point[1])
    H, W = grey.shape[:2]
    resp = []
    for sg in sigmas:
        r = int(math.ceil(4 * sg)) + 2
        x0, y0, x1, y1 = int(x) - r, int(y) - r, int(x) + r + 1, int(y) + r + 1
        if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
            break
        crop = grey[y0:y1, x0:x1].astype(np.float32)
        lap = cv2.Laplacian(cv2.GaussianBlur(crop, (0, 0), sg), cv2.CV_32F, ksize=3)
        resp.append(abs(float(cv2.getRectSubPix(lap, (1, 1), (x - x0, y - y0))[0, 0])) * sg * sg)
    if len(resp) < 3:
        return None
    i = int(np.argmax(resp))
    if i == 0 or i == len(resp) - 1 or resp[i] < 4.0:
        return None
    return float(2.83 * sigmas[i])


class _Scaled:
    """Frames of one object at the scale where its template fits TEMPLATE_MAX (shared per scale)."""

    def __init__(self, win: Window):
        self.win, self._cache = win, {}

    def get(self, k: float) -> tuple[dict[int, np.ndarray], tuple[float, float]]:
        """({frame: image}, (sx, sy)) with sx = image width / ORIGINAL width."""
        k = round(min(1.0, k), 2)
        if k not in self._cache:
            ww, wh = self.win.work_size
            size = (max(8, round(ww * k)), max(8, round(wh * k)))
            imgs = self.win.work if size == (ww, wh) else {
                f: cv2.resize(im, size, interpolation=cv2.INTER_AREA) for f, im in self.win.work.items()}
            self._cache[k] = (imgs, (size[0] / self.win.size[0], size[1] / self.win.size[1]))
        return self._cache[k]


def _guide(anchors: list[Anchor], S: np.ndarray):
    fr = np.array([a.frame for a in anchors], float)
    P = np.array([a.centre for a in anchors]) * S - 0.5
    return lambda f: np.array([np.interp(f, fr, P[:, 0]), np.interp(f, fr, P[:, 1])])


def _tsize(a: Anchor, S: np.ndarray) -> tuple[int, int]:
    return _odd(a.wh[0] * S[0]), _odd(a.wh[1] * S[1])


def _segment(imgs, a: Anchor, b: Anchor, S: np.ndarray, guide, d_tol: float = math.inf,
             weights: dict | None = None) -> tuple[dict | None, dict]:
    """Forward pass from a, backward pass from b, fused -> ({frame: centre (a's reference, scaled
    px)}, info with the offset d = b's reference - a's reference) or (None, info) when inconsistent:
    the passes' offset varies by more than FB_TOL, or is itself larger than an annotator's box placement
    can explain (|d| > max(d_tol, D_TOL x template side): the passes followed different things).
    weights: {anchor frame: template pixel weights} (template_weight)."""
    tsize, bsize = _tsize(a, S), _tsize(b, S)
    ca, cb = a.centre * S - 0.5, b.centre * S - 0.5
    weights = weights or {}
    pf = track_pass(imgs, a.frame, b.frame, ca, tsize, guide, weights.get(a.frame))
    pb = track_pass(imgs, b.frame, a.frame, cb, bsize, guide, weights.get(b.frame))
    span = b.frame - a.frame
    common = sorted(set(pf) & set(pb))
    info = {"a": a.frame, "b": b.frame, "n_common": len(common)}
    if not common or len(common) < max(2, 0.5 * (span + 1)):
        return None, {**info, "why": "lost"}
    d = np.array([pb[f][0] - pf[f][0] for f in common])
    dm = np.median(d, axis=0)
    spread = float(np.max(np.linalg.norm(d - dm, axis=1)))
    tol = max(FB_TOL_MIN, FB_TOL * max(*tsize, *bsize))
    info.update(spread=round(spread, 3), tol=round(tol, 2), d=[round(float(x), 2) for x in dm])
    if spread > tol:
        return None, {**info, "why": "fb"}
    if float(np.linalg.norm(dm)) > max(d_tol, D_TOL * max(*tsize, *bsize)):
        return None, {**info, "why": "offset"}
    fused = {}
    for f in range(a.frame, b.frame + 1):
        w = (f - a.frame) / span if span else 0.0
        if f in pf and f in pb:
            fused[f] = (1 - w) * pf[f][0] + w * (pb[f][0] - dm)
        elif f in pf:
            fused[f] = pf[f][0]
        elif f in pb:
            fused[f] = pb[f][0] - dm
    info["why"] = "ok"
    sig = max(LINK_SIG_MIN, LINK_SIG * max(*tsize, *bsize), 0.5 * spread)
    return {"path": fused, "d": dm, "sig": sig}, info


def _fuse_offsets(m: np.ndarray, d: np.ndarray, sig_d: np.ndarray, sig_a: float, iters: int = 4) -> np.ndarray:
    """Offsets e_k (K+1 x 2) minimising sum |e_{k+1} - e_k + d_k|^2 / sig_d_k^2 + sum rho(|e_k - m_k| / sig_a)
    (rho Huber at 2 sig_a, by IRLS): the chained template offsets d (precise, but each link can carry
    a small bias) fused with the annotator's anchors m (noisy; robust to outliers)."""
    n = len(m)
    w = np.ones(n)
    e = m.copy()
    for _ in range(iters):
        A = np.zeros((n - 1 + n, n))
        rhs = np.zeros((n - 1 + n, 2))
        for k in range(n - 1):
            A[k, k + 1], A[k, k] = 1 / sig_d[k], -1 / sig_d[k]
            rhs[k] = -d[k] / sig_d[k]
        for k in range(n):
            A[n - 1 + k, k] = math.sqrt(w[k]) / sig_a
            rhs[n - 1 + k] = math.sqrt(w[k]) * m[k] / sig_a
        e = np.linalg.lstsq(A, rhs, rcond=None)[0]
        r = np.linalg.norm(e - m, axis=1) / sig_a
        w = np.where(r <= 2.0, 1.0, 2.0 / np.maximum(r, 1e-9))
    return e


def chain_scale(chain: np.ndarray, refs: np.ndarray, sig: float) -> tuple[float, float, np.ndarray]:
    """Slope (with its standard error, and the direction) of the annotator's points `refs` regressed
    on the chained positions `chain` (both K x 2, original px) along the chain's main direction: 1
    when the chain spans what the annotator saw. The error uses the annotator's prior noise `sig`
    (per axis), not the scatter about the fit: an annotator's over-regular points (equal steps of a
    slow object) must not make a small disagreement look significant."""
    c = chain - chain.mean(axis=0)
    if len(c) < 2 or not np.any(c):
        return 1.0, math.inf, np.array([1.0, 0.0])
    u = np.linalg.svd(c, full_matrices=False)[2][0]
    x, y = c @ u, (refs - refs.mean(axis=0)) @ u
    sxx = float(x @ x)
    if sxx <= 1e-9:
        return 1.0, math.inf, u
    return float(x @ y) / sxx, sig / math.sqrt(sxx), u


def dense_motion(win: Window, obs: list[Obs], fps: float, size_hint=None, seen_scale: float = 1.0
                 ) -> tuple[dict[int, list[float]] | None, dict]:
    """Dense path ({frame: [x, y]} in original px, one per tracked frame) of the object annotated by
    `obs`, or (None, info with the reason). seen_scale: annotator image px per original px (meta
    "scale"), which sets the residual tolerance in the pixels the annotator saw."""
    sx = win.work_size[0] / win.size[0]
    grey: dict[int, np.ndarray] = {}

    def probe(f, point):
        if f not in win.work:
            return None
        if f not in grey:
            grey[f] = cv2.cvtColor(win.work[f], cv2.COLOR_BGR2GRAY)
        d = blob_size(grey[f], np.asarray(point, float) * sx - 0.5, 0.25 * min(win.work_size))
        return d / sx if d else None

    anchors, notes = anchors_from_obs(obs, fps, size_hint, probe)
    info: dict = {"n_anchors": len(anchors), "notes": notes}
    if "no_size" in notes:
        return None, {**info, "why": "no_size"}
    if len(anchors) < 2:
        return None, {**info, "why": "few_anchors"}
    if any(a.frame not in win.work for a in anchors):
        return None, {**info, "why": "frames"}
    size_orig = float(np.median([max(a.wh) for a in anchors]))
    sc = _Scaled(win)
    k = min(1.0, TEMPLATE_MAX / max(1.0, size_orig * win.work_size[0] / win.size[0]))
    imgs, S = sc.get(k)
    S = np.asarray(S)
    guide = _guide(anchors, S)
    info["k"] = round(k * win.work_size[0] / win.size[0], 4)
    sig_a = max(ANCHOR_SIG / max(seen_scale, 1e-6), ANCHOR_SIG_SIZE * size_orig)   # original px
    d_tol = 4.5 * sig_a * float(S.min())   # object px: the difference of two anchors, 3 sd
    weights, how = {}, []
    for a in anchors:
        weights[a.frame], h = template_weight(imgs[a.frame], a.centre * S - 0.5, _tsize(a, S))
        how.append(h)
    info["mask"] = {h: how.count(h) for h in sorted(set(how))}
    # chain segments; an anchor whose both segments fail is skipped once (annotator outlier)
    pieces, cur, segs, skipped = [], None, [], []
    i = 0

    def link(a, b):   # object-weighted templates, else (a split or wrong mask loses the object) whole boxes
        res, si = _segment(imgs, a, b, S, guide, d_tol, weights)
        if res is None and any(weights.get(x.frame) is not None for x in (a, b)):
            res2, si2 = _segment(imgs, a, b, S, guide, d_tol)
            if res2 is not None:
                return res2, {**si2, "unweighted": True}
        return res, si

    while i < len(anchors) - 1:
        a = anchors[i]
        res, si = link(a, anchors[i + 1])
        j = i + 1
        if res is None and i + 2 < len(anchors):
            res2, si2 = link(a, anchors[i + 2])
            if res2 is not None:
                res, si, j = res2, si2, i + 2
                skipped.append(anchors[i + 1].frame)
        segs.append(si)
        if res is None:
            cur = None
        else:
            if cur is None:
                cur = {"anchors": [i], "segs": []}
                pieces.append(cur)
            cur["segs"].append(res)
            cur["anchors"].append(j)
        i = j
    info.update(segments=segs, skipped=skipped)
    span = anchors[-1].frame - anchors[0].frame
    covered = sum(anchors[p["anchors"][-1]].frame - anchors[p["anchors"][0]].frame for p in pieces)
    info["cover"] = round(covered / span, 3) if span else 0.0
    if not pieces or covered < MIN_COVER * span:
        return None, {**info, "why": "cover"}
    # per piece: the tracked path in the first anchor's template reference (segment n tracked anchor
    # n's reference, anchor 0's moved by d_0 + ... + d_{n-1}), its scale checked against the
    # annotator's points, then a smooth offset to the annotator's reference (_fuse_offsets)
    out: dict[int, list[float]] = {}
    resid, scales = [], []
    for p in pieces:
        idx = p["anchors"]
        d = np.array([seg["d"] / S for seg in p["segs"]])                    # original px
        sig_d = np.array([seg["sig"] / S.min() for seg in p["segs"]])
        shift = np.vstack([np.zeros(2), np.cumsum(d, axis=0)])
        P = {f: (x + 0.5) / S - shift[n] for n, seg in enumerate(p["segs"]) for f, x in seg["path"].items()}
        C = np.array([P[anchors[n].frame] for n in idx])
        refs = np.array([anchors[n].ref for n in idx])
        # a template that keeps some static background lags the object in every segment alike (the
        # forward-backward check cannot see that) and the chain shrinks the motion: its scale along
        # the motion is uncertain (prior sd SCALE_SIG), the annotator's points measure it too.
        # Rejected when it spans significantly less than the annotator's points (beta > 1: lag) or
        # runs against them. Spanning more is no lag: either a faster neighbour was followed, which
        # the residual check below sees in the annotator's own pixels, or the annotator under-read a
        # motion of a few pixels at its resolution (simulation_0196's bubble: equal 3 px steps, half
        # the motion that the chain, optical flow and the ground truth agree on)
        beta, se, u = chain_scale(C, refs, sig_a)
        scales.append([round(beta, 4), round(se, 4) if math.isfinite(se) else None])
        off = abs(beta - 1) > SCALE_Z * math.hypot(SCALE_SIG, se)
        if off and (beta > 1 or beta <= 0):
            return None, {**info, "scale": scales, "why": "scale"}
        r = (SCALE_SIG / se) ** 2 if math.isfinite(se) else 0.0
        b = (1 + r * beta) / (1 + r)                                         # combined scale
        c0 = C.mean(axis=0)
        P = {f: q + (b - 1) * float((q - c0) @ u) * u for f, q in P.items()}
        C = np.array([P[anchors[n].frame] for n in idx])
        e = _fuse_offsets(refs - C, np.zeros_like(d), sig_d, sig_a)
        for n, seg in enumerate(p["segs"]):
            fa, fb = anchors[idx[n]].frame, anchors[idx[n + 1]].frame
            for f in seg["path"]:
                w = (f - fa) / (fb - fa)
                q = P[f] + (1 - w) * e[n] + w * e[n + 1]
                out[f] = [round(float(q[0]), 3), round(float(q[1]), 3)]
        scales[-1].append(round(b, 4))
        ends = [anchors[n] for n in range(idx[0], idx[-1] + 1)]
        resid += [float(np.linalg.norm(a.ref - np.asarray(out[a.frame]))) for a in ends if a.frame in out]
    med = float(np.median(resid))
    tol = RESID_TOL * ANCHOR_SIG / max(seen_scale, 1e-6)
    inside = float(np.mean(np.asarray(resid) <= 2 * tol))
    info.update(resid_med=round(med, 2), resid_max=round(max(resid), 2), resid_tol=round(tol, 2),
                resid_inside=round(inside, 3), n_pieces=len(pieces), size=round(size_orig, 1), scale=scales)
    if med > tol or inside < RESID_INSIDE:
        return None, {**info, "why": "residual"}
    # anchors outside the tracked pieces keep the annotator's point (the path stays in its reference)
    filled = [a for a in anchors if a.frame not in out and not any(
        anchors[p["anchors"][0]].frame <= a.frame <= anchors[p["anchors"][-1]].frame for p in pieces)]
    for a in filled:
        out[a.frame] = [round(float(a.ref[0]), 3), round(float(a.ref[1]), 3)]
    info["n_filled"] = len(filled)
    info["why"] = "ok"
    return dict(sorted(out.items())), info


def motion_obs(path: dict[int, list[float]], obs: list[Obs], fps: float) -> list[Obs]:
    """Dense point obs (t = frame / fps) + the original obs without their points (boxes, extents
    kept), as qp.refine does."""
    dense = [Obs(t=f / fps, point=list(p)) for f, p in sorted(path.items())]
    return dense + [Obs(t=o.t, extent=o.extent, box=o.box, score=o.score) for o in obs
                    if o.extent is not None or o.box is not None]


# --------------------------------------------------------------------------- size


def _seg_crop_box(box, W: int, H: int) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = box
    m = SIZE_MARGIN * max(x1 - x0, y1 - y0) + 6
    return (int(math.floor(x0 - m)), int(math.floor(y0 - m)), int(math.ceil(x1 + m)), int(math.ceil(y1 + m)))


def grabcut_extent(crop: np.ndarray, box_in_crop, mode: str, name: str = "") -> tuple[list | None, dict]:
    """Extent ([[x1, y1], [x2, y2]] in crop px, continuous coordinates) of the object in `box_in_crop`
    by GrabCut, or (None, info) when unreliable."""
    from .open.cv_track import ROUND_FILL, clean_mask, extent_from_features, mask_features

    h, w = crop.shape[:2]
    k = min(1.0, SIZE_MAX_SIDE / max(h, w))
    img = crop if k >= 1 else cv2.resize(crop, (max(1, round(w * k)), max(1, round(h * k))),
                                         interpolation=cv2.INTER_AREA)
    kx, ky = img.shape[1] / w, img.shape[0] / h
    x0, y0, x1, y1 = box_in_crop
    px, py = SIZE_RECT_PAD * (x1 - x0) + 1, SIZE_RECT_PAD * (y1 - y0) + 1
    rx0, ry0 = max(1, int(math.floor((x0 - px) * kx))), max(1, int(math.floor((y0 - py) * ky)))
    rx1 = min(img.shape[1] - 1, int(math.ceil((x1 + px) * kx)))
    ry1 = min(img.shape[0] - 1, int(math.ceil((y1 + py) * ky)))
    if rx1 - rx0 < 4 or ry1 - ry0 < 4:
        return None, {"why": "small"}
    # dither (fixed seed): a floor on the colour models' covariance, else on flat regions (renders,
    # skies) a pixel two grey levels off the background colour has no background likelihood at all
    noise = np.random.default_rng(0).normal(0.0, 2.0, img.shape)
    img = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    mask = np.zeros(img.shape[:2], np.uint8)
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    try:
        cv2.setRNGSeed(0)   # GrabCut seeds its colour models by k-means on OpenCV's global RNG
        cv2.grabCut(img, mask, (rx0, ry0, rx1 - rx0, ry1 - ry0), bgd, fgd, 5, cv2.GC_INIT_WITH_RECT)
    except cv2.error:
        return None, {"why": "grabcut_error"}
    fg = clean_mask((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD))
    f = mask_features(fg, clean=False)
    if f is None:
        return None, {"why": "empty"}
    fill = f["area"] / float((rx1 - rx0) * (ry1 - ry0))
    bx0, by0, bx1, by1 = f["box"]
    touch = sum([bx0 <= rx0, by0 <= ry0, bx1 >= rx1, by1 >= ry1])
    info = {"fill": round(fill, 3), "touch": touch}
    if not SIZE_FILL[0] <= fill <= SIZE_FILL[1]:
        return None, {**info, "why": "fill"}
    if touch == 4:
        return None, {**info, "why": "touch"}
    # sub-pixel boundary: the mask takes whole pixels and, with 4:2:0 chroma, about one blurred pixel
    # of fringe per side; a round object's area is re-counted with fractional (alpha) boundary pixels,
    # other extents' endpoints snap to the colour edge along their line (within +-SIZE_SNAP px)
    clean = crop if k >= 1 else cv2.resize(crop, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_AREA)
    soft = soft_area(clean, fg)
    if soft is not None and mode in ("diameter", "radius"):
        info["soft_area"] = round(soft / max(f["area"], 1), 4)
        f = {**f, "area": soft}
    ext = extent_from_features(f, mode, name)
    _, _, L, S, _ = f["rect"]
    by_area = mode in ("diameter", "radius") and L <= 1.25 * S and f["area"] < ROUND_FILL * L * S
    if not by_area:   # (extent_from_features' round case: an equivalent-circle diameter)
        snapped, si = snap_extent(clean, ext, SIZE_SNAP)
        if snapped is not None:
            info["snap"] = [si.get("end0"), si.get("end1")]
            ext = snapped
    return [[ext[0][0] / kx, ext[0][1] / ky], [ext[1][0] / kx, ext[1][1] / ky]], {**info, "why": "ok"}


def soft_area(img: np.ndarray, mask: np.ndarray) -> float | None:
    """Mask area with fractional boundary pixels: alpha = position of the pixel's colour between the
    object's and the surrounding background's median colours, over a 2-px band around the mask edge.
    None when the object is not uniform enough (or too close to its background) for that model."""
    m = mask.astype(np.uint8)
    k3 = np.ones((3, 3), np.uint8)
    inner = cv2.erode(m, k3, iterations=2).astype(bool)
    dil = cv2.dilate(m, k3, iterations=2).astype(bool)
    ring = cv2.dilate(m, k3, iterations=5).astype(bool) & ~dil
    band = dil & ~inner
    if inner.sum() < 9 or ring.sum() < 9:
        return None
    px = img.astype(np.float32)
    fgc, bgc = np.median(px[inner], axis=0), np.median(px[ring], axis=0)
    v = fgc - bgc
    vv = float(v @ v)
    if vv < 20.0 ** 2:
        return None
    proj = (px[inner] - bgc) @ v / vv
    if float(np.median(np.abs(proj - np.median(proj)))) > 0.15:   # textured: no single object colour
        return None
    alpha = np.clip((px[band] - bgc) @ v / vv, 0.0, 1.0)
    return float(inner.sum() + alpha.sum())


def _length(e) -> float:
    return math.hypot(e[1][0] - e[0][0], e[1][1] - e[0][1])


def snap_extent(crop: np.ndarray, ext_in_crop, search: float) -> tuple[list | None, dict]:
    """The annotator's extent with each endpoint moved to the strongest edge along the extent's line
    within +-`search` px (sub-pixel), or kept where no clear edge is found."""
    e = np.asarray(ext_in_crop, float)
    L = float(np.linalg.norm(e[1] - e[0]))
    if L < 3:
        return None, {"why": "short"}
    u = (e[1] - e[0]) / L
    n = np.array([-u[1], u[0]])
    step = 0.25
    s = np.arange(-search, L + search + step / 2, step)
    grey = cv2.GaussianBlur(crop, (0, 0), 0.8).astype(np.float32)
    prof = 0.0
    for off in (-1.0, 0.0, 1.0):  # three parallel lines
        pts = (e[0][None] + s[:, None] * u[None] + off * n[None] - 0.5).astype(np.float32)
        smp = cv2.remap(grey, pts[:, 0].reshape(1, -1), pts[:, 1].reshape(1, -1), cv2.INTER_LINEAR,
                        borderMode=cv2.BORDER_REPLICATE).reshape(len(s), -1)
        prof = prof + smp
    g = np.linalg.norm(np.gradient(prof / 3.0, step, axis=0).reshape(len(s), -1), axis=1)
    inner = g[(s > search) & (s < L - search)] if L > 2 * search + 2 else g
    floor = float(np.median(inner)) if len(inner) else 0.0
    out, info = e.copy(), {}
    for end, (lo, hi) in ((0, (-search, search)), (1, (L - search, L + search))):
        sel = np.flatnonzero((s >= lo) & (s <= hi))
        i = sel[np.argmax(g[sel])]
        peak = float(g[i])
        if peak < max(6.0, 2.5 * floor):
            info[f"end{end}"] = "weak"
            continue
        di = _peak_offset(g[i - 1], g[i], g[i + 1]) if 0 < i < len(g) - 1 else 0.0
        out[end] = e[0] + (s[i] + di * step) * u
        info[f"end{end}"] = round(float(s[i] + di * step - (0 if end == 0 else L)), 2)
    return out.tolist(), {**info, "why": "ok"}


def dense_size(win: Window, obs: list[Obs], fps: float, dimension: str, name: str = "",
               method: str = SIZE_METHOD, seen_scale: float = 1.0) -> tuple[list[Obs] | None, dict]:
    """Obs with re-measured extents (original px) on the annotated frames with a box (snap: with an
    extent); obs whose re-measurement fails keep the annotator's extent. None when nothing was
    re-measured."""
    from .open.cv_track import dimension_mode

    mode = dimension_mode(dimension, name)
    if mode is None:
        return None, {"why": "no_dimension"}
    W, H = win.size
    out, infos, n_new = [], [], 0
    for o in obs:
        f = int(round(o.t * fps))
        new, inf = None, {"frame": f}
        if o.box is not None and (method == "grabcut" or o.extent is not None):
            cb = _seg_crop_box(o.box, W, H)
            key = next((k for k in win.crops if k[0] == f and k[1:] == (max(0, cb[0]), max(0, cb[1]),
                                                                          min(W, cb[2]), min(H, cb[3]))), None)
            if key is not None:
                crop, (x0, y0) = win.crops[key], key[1:3]
                if method == "grabcut":
                    e, i2 = grabcut_extent(crop, [o.box[0] - x0, o.box[1] - y0, o.box[2] - x0, o.box[3] - y0],
                                           mode, name)
                else:
                    search = max(3.0 / max(seen_scale, 1e-6), 0.08 * _length(o.extent))
                    e, i2 = snap_extent(crop, [[p[0] - x0, p[1] - y0] for p in o.extent], search)
                inf.update(i2)
                if e is not None:
                    new = [[e[0][0] + x0, e[0][1] + y0], [e[1][0] + x0, e[1][1] + y0]]
        if new is not None:   # vs the annotator's extent, else the box side qp.geometry would use
            w, h = (o.box[2] - o.box[0], o.box[3] - o.box[1]) if o.box is not None else (0.0, 0.0)
            ref = _length(o.extent) if o.extent is not None else (
                h if mode == "vertical" else w if mode == "horizontal" else max(w, h))
            r = _length(new) / max(ref, 1e-9)
            inf["ratio"] = round(r, 3)
            if not SIZE_RATIO[0] <= r <= SIZE_RATIO[1]:
                inf["why"], new = "ratio", None
        if new is not None:
            n_new += 1
            out.append(Obs(t=o.t, point=o.point, extent=[[round(v, 2) for v in p] for p in new], box=o.box,
                           score=o.score))
        else:
            out.append(o)
        infos.append(inf)
    info = {"mode": mode, "method": method, "frames": infos, "n_new": n_new}
    if n_new == 0:
        return None, {**info, "why": "none"}
    return out, {**info, "why": "ok"}


# --------------------------------------------------------------------------- annotations


def _obs_key(obs: list[Obs]) -> list:
    r = lambda v: None if v is None else [round(float(x), 1) for x in np.ravel(v)]  # noqa: E731
    return [[round(o.t, 4), r(o.point), r(o.box), r(o.extent)] for o in obs]


def _key(*parts) -> str:
    return hashlib.sha1(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()[:20]


_SIZE_ONLY = ("SIZE_",)
_MOTION_ONLY = ("TEMPLATE_", "MASK_", "NCC_", "MAX_COAST", "FB_", "MIN_COVER", "LINK_", "ANCHOR_", "RESID_",
                "D_TOL", "SCALE_", "BORROW_", "WORK_")


def _settings(kind: str) -> dict:
    """The module constants a result of this kind depends on (part of its cache key)."""
    skip = _SIZE_ONLY if kind == "motion" else _MOTION_ONLY
    return {k: v for k, v in globals().items() if k.isupper() and isinstance(v, (int, float, str, tuple))
            and not k.startswith(skip) and k != "MOTION"}


class Cache:
    """{key: result} per video in <dir>/<video stem>.json (no directory: in memory only). Several
    processes may share a directory: a save merges the file's current entries and replaces it
    atomically (unique temp file); an unreadable file is moved aside (<stem>.json.bad) and treated
    as empty, so it costs a recomputation, never the video."""

    def __init__(self, directory: str | Path | None):
        self.dir = Path(directory) if directory else None
        self.mem: dict[str, dict] = {}

    def _file(self, path: str) -> Path | None:
        return self.dir / f"{Path(path).stem.strip()}.json" if self.dir else None

    @staticmethod
    def _read(f: Path) -> dict:
        try:
            data = json.loads(f.read_text())
            if not isinstance(data, dict):
                raise ValueError("not a JSON object")
            return data
        except FileNotFoundError:
            return {}
        except (OSError, ValueError) as e:   # JSONDecodeError and UnicodeDecodeError are ValueErrors
            warnings.warn(f"dense-track cache {f} unreadable ({type(e).__name__}: {e}); moved aside")
            with contextlib.suppress(OSError):
                os.replace(f, f.with_name(f.name + ".bad"))
            return {}

    def load(self, path: str) -> dict:
        f = self._file(path)
        if path not in self.mem:
            self.mem[path] = self._read(f) if f is not None else {}
        return self.mem[path]

    def save(self, path: str) -> None:
        f = self._file(path)
        if f is None:
            return
        f.parent.mkdir(parents=True, exist_ok=True)
        data = {**self._read(f), **self.mem.get(path, {})}   # keep what other processes added meanwhile
        fd, tmp = tempfile.mkstemp(dir=f.parent, prefix=f".{f.stem}.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as fh:
                json.dump(data, fh)
            os.replace(tmp, f)
        except BaseException:
            with contextlib.suppress(OSError):
                os.unlink(tmp)
            raise
        self.mem[path] = data


def _role_quantity(a, role: str):
    return a.spec.prior if role.startswith("prior") else a.spec.target


@dataclass
class Job:
    """One track to densify: kind "motion" (dense points) or "size" (re-measured extents)."""
    kind: str
    obs: list[Obs]
    fps: float
    image_size: tuple[int, int]
    seen_scale: float = 1.0
    name: str = ""
    dimension: str = ""

    def key(self, fid, size_method: str, sizes=()) -> str:
        """Cache key: everything the result depends on (sizes: the boxes borrowed from the object's
        other tracks, borrowed_sizes)."""
        if self.kind == "motion":
            extra = (self.name.strip().casefold(), [[round(t, 4), round(w, 1), round(h, 1)] for t, (w, h) in sizes])
        else:
            extra = (self.dimension, self.name, size_method)
        return _key(self.kind, fid, round(self.fps, 6), round(self.seen_scale, 4), _obs_key(self.obs), extra,
                    _settings(self.kind), VERSION)


def plan(anns: dict, roles=("prior", "prior2", "target", "target2"), what: str = "motion",
         motion_kinds=MOTION) -> list[tuple[int, object, RoleTrack, str]]:
    """(qid, annotation, track, "motion" | "size") jobs: motion for tracks of a motion quantity with
    >= 2 located frames, size for tracks of a size quantity with a box on some frame."""
    jobs = []
    for qid, a in anns.items():
        for tr in a.tracks:
            if tr.role not in roles:
                continue
            q = _role_quantity(a, tr.role)
            if what in ("motion", "both") and q.kind in motion_kinds and \
                    len({round(o.t, 4) for o in tr.obs if o.point is not None or o.box is not None}) >= 2:
                jobs.append((qid, a, tr, "motion"))
            if what in ("size", "both") and q.kind in ("size", "other") and \
                    any(o.box is not None for o in tr.obs):
                jobs.append((qid, a, tr, "size"))
    return jobs


def size_hints(tracks: list[RoleTrack]) -> dict[str, list[tuple[float, tuple[float, float], tuple[float, float]]]]:
    """object name (casefolded) -> [(t, (w, h), (box centre x, y))]: the boxes of every track of a video."""
    out: dict[str, list] = {}
    for tr in tracks:
        for o in tr.obs:
            b = o.box
            if b is not None and b[2] > b[0] and b[3] > b[1]:
                out.setdefault(tr.object.strip().casefold(), []).append(
                    (float(o.t), (b[2] - b[0], b[3] - b[1]), ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)))
    return _sorted_unique(out)


def _sorted_unique(hints: dict) -> dict:
    return {k: sorted({(t, tuple(map(float, wh)), tuple(map(float, c))) for t, wh, c in v}) for k, v in hints.items()}


BORROW_OFF = 0.35   # a box borrowed from another track sizes this one only if this track's point (at the
                    # box's time) lies within this share of the box's width / height of its centre


def borrowed_sizes(obs: list[Obs], boxes) -> list[tuple[float, tuple[float, float]]]:
    """[(t, (w, h))] of the boxes (size_hints rows of the same object name) that frame this track's
    object: at the box's time (inside the track's annotated span) the track's point, interpolated,
    lies near the box centre. A box of another object of the same name, or one placed elsewhere,
    would size the template wrongly."""
    pts = sorted((o.t, o.point) for o in obs if o.point is not None)
    if not pts or not boxes:
        return []
    ts = np.array([t for t, _ in pts])
    xy = np.array([p for _, p in pts], float)
    gap = float(np.median(np.diff(ts))) if len(ts) > 1 else 0.0
    out = []
    for t, (w, h), (cx, cy) in boxes:
        if not ts[0] - gap - 1e-6 <= t <= ts[-1] + gap + 1e-6:
            continue
        px, py = np.interp(t, ts, xy[:, 0]), np.interp(t, ts, xy[:, 1])
        if abs(px - cx) <= BORROW_OFF * w and abs(py - cy) <= BORROW_OFF * h:
            out.append((float(t), (float(w), float(h))))
    return out


def run_video(path: str, jobs: list[Job], hints: dict | None = None, cache_dir: str | Path | None = None,
              size_method: str = SIZE_METHOD) -> list[dict]:
    """Results for the jobs of one video, in order: {"path": {frame: [x, y]} | None, "info"} (motion)
    or {"extents": [extent per obs] | None, "info"} (size). One decode serves all uncached jobs."""
    cache = Cache(cache_dir)
    store = cache.load(path)
    fid = (Path(path).name, Path(path).stat().st_size)
    sizes = [borrowed_sizes(j.obs, (hints or {}).get(j.name.strip().casefold(), [])) if j.kind == "motion" else []
             for j in jobs]
    keys = [j.key(fid, size_method, sz) for j, sz in zip(jobs, sizes)]
    missing = [(k, j, sz) for k, j, sz in zip(keys, jobs, sizes) if k not in store]
    if missing:
        frames, crops = set(), {}
        for _, j, _ in missing:
            fr = [int(round(o.t * j.fps)) for o in j.obs if o.point is not None or o.box is not None]
            if j.kind == "motion" and fr:
                frames.update(range(min(fr), max(fr) + 1))
            elif j.kind == "size":
                for o in j.obs:
                    if o.box is not None:
                        crops.setdefault(int(round(o.t * j.fps)), set()).add(_seg_crop_box(o.box, *j.image_size))
        win = decode(path, frames, {f: sorted(c) for f, c in crops.items()})
        for k, j, h in missing:
            if k in store:
                continue
            try:
                if j.kind == "motion":
                    hint = (lambda f, h=h, fps=j.fps: min(h, key=lambda x: (abs(x[0] - f / fps), x[0]))[1]) if h else None
                    path_px, info = dense_motion(win, j.obs, j.fps, hint, j.seen_scale)
                    store[k] = {"path": path_px, "info": info}
                else:
                    new, info = dense_size(win, j.obs, j.fps, j.dimension, j.name, size_method, j.seen_scale)
                    store[k] = {"extents": None if new is None else [o.extent for o in new], "info": info}
            except (cv2.error, ValueError, IndexError, KeyError, ZeroDivisionError) as e:
                store[k] = {"path": None, "extents": None, "info": {"why": f"error:{type(e).__name__}:{e}"}}
        cache.save(path)
    return [store[k] for k in keys]


def _init_worker() -> None:
    """Pool workers: one OpenCV thread each (the pool parallelises over videos)."""
    cv2.setNumThreads(1)


def _run_video_safe(args) -> list[dict] | str:
    try:
        return run_video(*args)
    except Exception as e:  # noqa: BLE001 - reported per video by the caller
        return f"error:{type(e).__name__}:{e}"


def apply_result(tr: RoleTrack, kind: str, res: dict, fps: float) -> bool:
    """Replace the track's obs by an accepted result (source "dense"); False when not accepted."""
    if kind == "motion" and res.get("path"):
        tr.obs = motion_obs({int(f): p for f, p in res["path"].items()}, tr.obs, fps)
    elif kind == "size" and res.get("extents"):
        tr.obs = [Obs(t=o.t, point=o.point, extent=e if e is not None else o.extent, box=o.box, score=o.score)
                  for o, e in zip(tr.obs, res["extents"])]
    else:
        return False
    tr.source = "dense"
    return True


def densify_annotations(anns: dict, video_paths: dict[int, str], video_meta: dict[int, tuple],
                        what: str = "motion", cache_dir: str | Path | None = None, log: list | None = None,
                        roles=("prior", "prior2", "target", "target2"), size_method: str = SIZE_METHOD,
                        motion_kinds=MOTION, workers: int = 1, skip=()) -> dict:
    """In place: densify the tracks of {qid: Annotation} (qp.claude_annotate). video_paths: qid ->
    local video; video_meta: qid -> (fps, (W, H)) or (fps, (W, H), seen_scale: annotator image px
    per original px). what: "motion" | "size" | "both". skip: (qid, role) pairs left alone. Accepted
    tracks get source "dense" and the annotation flag dense_motion / dense_size; a video that fails
    keeps its tracks (flag dense_error). `log` collects (qid, role, kind, info). Returns anns."""
    by_video: dict[str, list] = {}
    for qid, a, tr, kind in plan(anns, roles, what, motion_kinds):
        if (qid, tr.role) in skip or not video_paths.get(qid) or qid not in video_meta:
            continue
        m = video_meta[qid]
        q = _role_quantity(a, tr.role)
        job = Job(kind, list(tr.obs), float(m[0]), tuple(int(v) for v in m[1]),
                  float(m[2]) if len(m) > 2 and m[2] else 1.0, tr.object, q.dimension)
        by_video.setdefault(video_paths[qid], []).append((qid, a, tr, job))
    tracks_of = {}
    for qid, a in anns.items():
        if video_paths.get(qid):
            tracks_of.setdefault(video_paths[qid], []).extend(a.tracks)
    args = [(path, [it[3] for it in items], size_hints(tracks_of.get(path, [])), cache_dir, size_method)
            for path, items in by_video.items()]
    results = None
    if workers > 1 and len(args) > 1:
        import multiprocessing
        from concurrent.futures import ProcessPoolExecutor
        from concurrent.futures.process import BrokenProcessPool
        # spawn: forking a process whose OpenCV thread pool has started can deadlock the children
        # (spawn re-imports the caller's main module: scripts need an `if __name__ == "__main__"` guard)
        try:
            with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("spawn"),
                                     initializer=_init_worker) as ex:
                results = list(ex.map(_run_video_safe, args))
        except (BrokenProcessPool, RuntimeError, OSError):
            results = None
    if results is None:
        results = [_run_video_safe(a) for a in args]
    for (path, items), res in zip(by_video.items(), results):
        for n, (qid, a, tr, job) in enumerate(items):
            r = {"info": {"why": res}} if isinstance(res, str) else res[n]
            if isinstance(res, str):
                a.flags = sorted(set(a.flags) | {"dense_error"})
            if log is not None:
                log.append((qid, tr.role, job.kind, r["info"]))
            if not isinstance(res, str) and apply_result(tr, job.kind, r, job.fps):
                a.flags = sorted(set(a.flags) | {f"dense_{job.kind}"})
    return anns


# --------------------------------------------------------------------------- overlays


def overlay(path: str, sparse: list[Obs], dense: list[Obs], fps: float, out_png: str, n: int = 8,
            width: int = 480) -> None:
    """Montage of n frames spread over the dense track: dense path so far (yellow), current dense
    point (green), the annotator's point / box on its frames (red)."""
    pts = {int(round(o.t * fps)): o.point for o in dense if o.point is not None}
    ann = {int(round(o.t * fps)): o for o in sparse}
    if not pts:
        return
    fr = sorted(pts)
    show = sorted(set(np.linspace(fr[0], fr[-1], min(n, len(fr))).round().astype(int).tolist()))
    cap = cv2.VideoCapture(path)
    tiles, i = [], 0
    while i <= show[-1] and cap.grab():
        if i in show:
            ok, img = cap.retrieve()
            if ok:
                s = width / img.shape[1]
                img = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
                path_xy = np.array([pts[f] for f in fr if f <= i]) * s
                if len(path_xy) > 1:
                    cv2.polylines(img, [path_xy.round().astype(np.int32)], False, (0, 255, 255), 1)
                near = min(ann, key=lambda f: abs(f - i)) if ann else None
                if near is not None and abs(near - i) <= 1:
                    o = ann[near]
                    if o.box is not None:
                        b = (np.asarray(o.box) * s).round().astype(int)
                        cv2.rectangle(img, (b[0], b[1]), (b[2], b[3]), (0, 0, 255), 1)
                    if o.point is not None:
                        cv2.circle(img, tuple((np.asarray(o.point) * s).round().astype(int)), 4, (0, 0, 255), 1)
                if i in pts:
                    cv2.circle(img, tuple((np.asarray(pts[i]) * s).round().astype(int)), 2, (0, 255, 0), -1)
                cv2.putText(img, f"f{i}", (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                tiles.append(img)
        i += 1
    cap.release()
    if not tiles:
        return
    cols = 4
    blank = np.zeros_like(tiles[0])
    rows = [np.hstack(tiles[r:r + cols] + [blank] * (cols - len(tiles[r:r + cols]))) for r in range(0, len(tiles), cols)]
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_png), np.vstack(rows))
