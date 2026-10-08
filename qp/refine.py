"""Refine a motion PRIOR's point track with optical flow (pyramidal Lucas-Kanade, CPU).

The prior of a motion question sets the metric scale of every answer about its video, but an
annotator's points on a slow, small or low-contrast feature can be off by a large factor in total
motion (a bubble drifting 35 px inside a droplet, located on a different part of it from frame to
frame). Frame-to-frame optical flow measures exactly that motion to sub-pixel accuracy. Frames are
background-subtracted (per-pixel temporal median), so static edges do not pin the LK window.

Guards (any failure keeps the annotator's track):
  * static camera: the median share of pixels with |frame - background| > 12 is <= STATIC_MAX
  * the track stays finite and inside the image on every frame
  * forward-backward LK error <= FB_MAX_PX on EVERY consecutive frame pair
  * same direction as the annotator's net displacement (cos >= COS_MIN) when that exceeds 5 px
  * every annotated point lies within max(DEV_MIN_PX, object box size) of the flow track
On acceptance the track's points become one observation per frame from the annotator's first to
last point frame (boxes and extents are kept). Target tracks are never refined.

    refine_annotations(anns, {qid: video_path}, {qid: (fps, (width, height))})   # in place
"""

from __future__ import annotations

import math

import cv2
import numpy as np

from .spec import Obs

MOTION = ("speed", "acceleration", "displacement", "path_length")
LK = dict(winSize=(21, 21), maxLevel=4, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
STATIC_MAX = 0.15     # share of changed pixels above which the camera (or most of the scene) moves
CHANGE_GREY = 12      # grey levels: a pixel this far from the background has changed
BG_FRAMES = 60        # frames (evenly spaced) for the median background ...
BG_BYTES = 2.5e8      # ... fewer for large videos, so the sampled grey frames stay under ~250 MB
FB_MAX_PX = 1.0
COS_MIN = 0.8
DEV_MIN_PX = 30.0
GRID_PX = 3           # 3x3 grid of LK points this far apart around the start point


def _grey(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)


class VideoFlow:
    """Background model of one video (built once) and LK tracking on background-subtracted frames,
    decoded sequentially (memory: the BG_FRAMES sampled frames, then two frames at a time)."""

    def __init__(self, path: str):
        self.path = path
        cap = cv2.VideoCapture(path)
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if cap.isOpened() else 0
        if n <= 0 and cap.isOpened():
            while cap.grab():
                n += 1
            cap.release()
            cap = cv2.VideoCapture(path)
        pixels = max(1, int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) * cap.get(cv2.CAP_PROP_FRAME_HEIGHT))) if n else 1
        k = min(n, BG_FRAMES, max(15, int(BG_BYTES // pixels)))  # 60 frames up to ~4 MP, fewer for 4K
        want = set(np.linspace(0, max(n - 1, 0), k).round().astype(int).tolist()) if n else set()
        frames, i = [], 0
        while want and cap.isOpened() and cap.grab():
            if i in want:
                ok, img = cap.retrieve()
                if ok:
                    frames.append(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))  # uint8: 1 byte per pixel
                want.discard(i)
            i += 1
        cap.release()
        self.n_frames = n
        if not frames:
            self.bg, self.moving = None, math.inf
            return
        A = np.stack(frames)
        del frames
        self.bg = np.median(A, axis=0).astype(np.float32)
        self.moving = float(np.median([(np.abs(a.astype(np.float32) - self.bg) > CHANGE_GREY).mean() for a in A]))

    def _diff(self, img: np.ndarray) -> np.ndarray:
        return np.clip(128 + 2 * (_grey(img) - self.bg), 0, 255).astype(np.uint8)

    def track_many(self, reqs: list[tuple[int, list[float], int]]) -> list[tuple[dict | None, list[float]]]:
        """For each (f0, p0, f1): ({frame: (x, y)} from f0 to f1 starting at p0, moved rigidly by the
        median LK motion of a 3x3 point grid; forward-backward error per frame pair), or (None, [inf])
        when tracking is lost. One sequential decode serves all requests."""
        offs = np.array([[dx, dy] for dx in (-GRID_PX, 0, GRID_PX) for dy in (-GRID_PX, 0, GRID_PX)], np.float32)
        state = [{"pts": (np.asarray(p0, np.float32) + offs).reshape(-1, 1, 2), "path": {f0: np.asarray(p0, float)},
                  "fb": [], "lost": False} for f0, p0, _ in reqs]
        if not reqs:
            return []
        lo, hi = min(r[0] for r in reqs), max(r[2] for r in reqs)
        cap, prev, i = cv2.VideoCapture(self.path), None, 0
        try:
            while i <= hi and cap.grab():
                if i >= lo:
                    ok, img = cap.retrieve()
                    if not ok:
                        break
                    cur = self._diff(img)
                    for (f0, _, f1), st in zip(reqs, state):
                        if st["lost"] or not f0 < i <= f1:
                            continue
                        pts = st["pts"]
                        nxt, s1, _ = cv2.calcOpticalFlowPyrLK(prev, cur, pts, None, **LK)
                        back, s2, _ = cv2.calcOpticalFlowPyrLK(cur, prev, nxt, None, **LK)
                        good = (s1.ravel() == 1) & (s2.ravel() == 1)
                        if not good.any():
                            st["lost"] = True
                            continue
                        err = np.linalg.norm((back - pts).reshape(-1, 2), axis=1)
                        st["fb"].append(float(np.median(err[good])))
                        st["pts"] = pts + np.median((nxt - pts).reshape(-1, 2)[good], axis=0).reshape(1, 1, 2)
                        st["path"][i] = np.median(st["pts"].reshape(-1, 2), axis=0).astype(float)  # grid symmetric
                    prev = cur
                i += 1
        finally:
            cap.release()
        return [(None, [math.inf]) if st["lost"] or max(st["path"]) < f1 else (st["path"], st["fb"])
                for (_, _, f1), st in zip(reqs, state)]


def _request(flow: VideoFlow, fps: float, obs: list[Obs]) -> tuple[tuple | None, dict]:
    """(f0, p0, f1) to track for one motion track, or (None, reason)."""
    pts = [o for o in obs if o.point is not None]
    if len(pts) < 2:
        return None, {"why": "few_points"}
    info = {"moving": round(flow.moving, 3)}
    if flow.bg is None or not flow.moving <= STATIC_MAX:
        return None, {**info, "why": "camera_not_static"}
    fr = [int(round(o.t * fps)) for o in pts]
    if fr[-1] <= fr[0] or fr[0] < 0 or (flow.n_frames and fr[-1] >= flow.n_frames):
        return None, {**info, "why": "frames"}
    return (fr[0], pts[0].point, fr[-1]), info


def _accept(path, fb, fps: float, obs: list[Obs], image_size, info: dict) -> tuple[list[Obs] | None, dict]:
    """Dense refined obs from a flow track if every guard passes, else (None, info with the reason)."""
    pts = [o for o in obs if o.point is not None]
    fr = [int(round(o.t * fps)) for o in pts]
    W, H = image_size
    if path is None or not all(np.isfinite(p).all() and -5 <= p[0] <= W + 5 and -5 <= p[1] <= H + 5
                               for p in path.values()):
        return None, {**info, "why": "lost"}
    dev = max(float(np.linalg.norm(path[f] - np.asarray(o.point))) for f, o in zip(fr, pts))
    cd = np.asarray(pts[-1].point, float) - np.asarray(pts[0].point, float)
    ld = path[fr[-1]] - path[fr[0]]
    cos = float(cd @ ld / (np.linalg.norm(cd) * np.linalg.norm(ld) + 1e-9))
    boxes = [o.box for o in obs if o.box]
    size = float(np.median([max(b[2] - b[0], b[3] - b[1]) for b in boxes])) if boxes else 0.0
    info = {**info, "fb_max": round(max(fb), 3), "max_dev": round(dev, 1),
            "claude_disp": round(float(np.linalg.norm(cd)), 1), "lk_disp": round(float(np.linalg.norm(ld)), 1),
            "cos": round(cos, 2)}
    if max(fb) > FB_MAX_PX:
        return None, {**info, "why": "fb"}
    if np.linalg.norm(cd) > 5 and cos < COS_MIN:
        return None, {**info, "why": "direction"}
    if dev > max(DEV_MIN_PX, size):
        return None, {**info, "why": "deviation"}
    dense = [Obs(t=f / fps, point=[float(v) for v in path[f]]) for f in sorted(path)]
    return dense + [Obs(t=o.t, extent=o.extent, box=o.box, score=o.score) for o in obs
                    if o.extent is not None or o.box is not None], {**info, "why": "refined"}


def refine_track(flow: VideoFlow, fps: float, obs: list[Obs], image_size) -> tuple[list[Obs] | None, dict]:
    """Dense refined obs for one motion track, or (None, info with the reason) when a guard fails."""
    req, info = _request(flow, fps, obs)
    if req is None:
        return None, info
    path, fb = flow.track_many([req])[0]
    return _accept(path, fb, fps, obs, image_size, info)


def refine_annotations(anns: dict, video_paths: dict[int, str], video_meta: dict[int, tuple[float, tuple]],
                       roles=("prior", "prior2"), log: list | None = None) -> dict:
    """In place: refine the motion-prior tracks of every annotation ({qid: Annotation} as from
    qp.claude_annotate). video_paths / video_meta map qid -> local video path / (fps, (W, H)); a qid
    without a readable video is left alone. Adds flag 'prior_track_refined'. Each video is decoded
    twice (background, then one pass for all its tracks); `log` collects (qid, role, info). Never
    raises: an unexpected error on one video keeps that video's annotator tracks not yet replaced
    (flag 'prior_refine_error') and moves on."""
    jobs: dict[str, list] = {}
    for qid, a in anns.items():
        if not video_paths.get(qid) or qid not in video_meta or a.spec.prior.kind not in MOTION:
            continue
        for tr in a.tracks:
            if tr.role in roles:
                jobs.setdefault(video_paths[qid], []).append((qid, a, tr))
    for path, items in jobs.items():
        try:
            _refine_video(path, items, video_meta, log)
        except (cv2.error, ValueError):
            continue
        except Exception as e:  # noqa: BLE001 - a bad video must not stop a run's results
            for qid, a, tr in items:
                a.flags = sorted(set(a.flags) | {"prior_refine_error"})
                if log is not None:
                    log.append((qid, tr.role, {"why": f"error:{type(e).__name__}"}))
    return anns


def _refine_video(path: str, items: list, video_meta: dict, log: list | None) -> None:
    flow = VideoFlow(path)
    reqs, todo, index = [], [], {}
    for qid, a, tr in items:
        fps, size = video_meta[qid]
        req, info = _request(flow, fps, tr.obs)
        if req is None:
            if log is not None:
                log.append((qid, tr.role, info))
            continue
        key = (req[0], tuple(map(float, req[1])), req[2])  # tracks reused across questions: once
        if key not in index:
            index[key] = len(reqs)
            reqs.append(req)
        todo.append((qid, a, tr, fps, size, info, index[key]))
    results = flow.track_many(reqs)
    accepted = [(a, tr, *_accept(*results[k], fps, tr.obs, size, info), qid)
                for qid, a, tr, fps, size, info, k in todo]   # all guards first: no partial update
    for a, tr, new, info, qid in accepted:
        if log is not None:
            log.append((qid, tr.role, info))
        if new is not None:
            tr.obs = new
            a.flags = sorted(set(a.flags) | {"prior_track_refined"})
