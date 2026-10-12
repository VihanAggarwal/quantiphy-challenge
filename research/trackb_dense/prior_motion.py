"""Prior-motion re-measurement for 2D clips with a motion prior, from open-model boxes only (CPU).

Per 2D question whose prior is a motion quantity (speed / acceleration / displacement / path length), the prior's
track is replaced by each candidate below and the question re-solved (qp.geometry.solve); the candidates' prior
measurements (px, px/s, px/s^2) are then combined by a rule fixed before scoring (choose()):

  sparse   Qwen's grounding boxes as they are (box centres; the qwen_geo baseline)
  clean    Qwen's boxes after a RANSAC consistency fit (quadratic / cubic in time): Qwen often re-grounds a
           neighbouring object on some frames (identity switches); inliers only
  klt      rigid KLT (dyn.klt_rigid) from the clean box nearest the middle of the track (foreground features
           only when the camera is static); gated: the two random feature halves agree within 4%, the path
           covers >= 90% of Qwen's span and stays within max(6 px, 0.5 box) of Qwen's clean centres (median,
           after a constant offset)
  mask     foreground component of a static-camera clip followed from the anchor (dyn.mask_track); gated by the
           same coverage / residual checks
  seg      white-background clips (X_segmented, or X's segmented twin: pixel-aligned re-render) -> the
           foreground mask followed from the anchor (dyn.seg_track); same gates
  cv       the SAM 2 (Grounding DINO) prior track of the same question when its boxes agree with Qwen's clean
           boxes (median IoU >= 0.5 over common times)
  dense    qp.dense_track on Qwen's boxes (Track A post-step; from the qwen_dense annotations)

Tracking results are cached per video under common.CACHE/prior_<split>/.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import pickle
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dyn  # noqa: E402
from tbcommon import CACHE  # noqa: E402
from qp import geometry as G  # noqa: E402
from qp.spec import Obs, RoleTrack  # noqa: E402

MOTION = ("speed", "acceleration", "displacement", "path_length")
RANSAC_ITERS = 400
CLEAN_MIN = 0.5           # a consensus set must hold >= this share of the boxes (else the track is kept)
HALVES_MAX = 0.04
COVER_MIN = 0.9
IOU_MIN = 0.5
AGREE = 0.08              # |log| within which two candidates agree
PRIORITY = ("seg", "klt", "mask", "cv", "dense", "clean", "sparse")


# --------------------------------------------------------------------------- Qwen box cleaning

def _centres(obs):
    t, c, s = [], [], []
    for o in obs:
        b = o.box if o.box is not None else None
        if b is None:
            continue
        t.append(float(o.t))
        c.append([(b[0] + b[2]) / 2, (b[1] + b[3]) / 2])
        s.append(min(abs(b[2] - b[0]), abs(b[3] - b[1])))
    o = np.argsort(t)
    return np.array(t)[o], np.array(c).reshape(-1, 2)[o], np.array(s)[o]


def clean_mask(t, C, S, px_tol=4.0, seed=0):
    """Boolean inlier mask of a RANSAC fit of the centres C(t) (degree 2 or 3 per axis). The consensus set with
    the most inliers wins; between sets within one inlier, the one that moves more (a motion prior moves)."""
    n = len(t)
    if n < 5:
        return np.ones(n, bool)
    tol = max(px_tol, 0.25 * float(np.median(S))) if len(S) else px_tol
    rng = np.random.default_rng(seed)
    T = (t - t.mean()) / max(np.ptp(t), 1e-9)
    best, best_key = np.ones(n, bool), (-1, -1.0)
    for it in range(RANSAC_ITERS):
        deg = 2 if it % 2 == 0 else 3
        idx = rng.choice(n, deg + 1, replace=False)
        if len(np.unique(T[idx])) < deg + 1:
            continue
        coef = np.polyfit(T[idx], C[idx], deg)
        res = np.linalg.norm(np.vander(T, deg + 1) @ coef - C, axis=1)
        inl = res <= tol
        if inl.sum() < deg + 2:
            continue
        coef = np.polyfit(T[inl], C[inl], deg)            # refit on the consensus set
        res = np.linalg.norm(np.vander(T, deg + 1) @ coef - C, axis=1)
        inl = res <= tol
        motion = float(np.ptp(C[inl], axis=0).max()) if inl.sum() else 0.0
        key = (int(inl.sum()), motion)
        if key[0] > best_key[0] + 1 or (abs(key[0] - best_key[0]) <= 1 and key[1] > best_key[1]):
            best, best_key = inl, key
    if best.sum() < max(4, CLEAN_MIN * n):
        return np.ones(n, bool)
    return best


# --------------------------------------------------------------------------- trajectories -> tracks

def traj_track(tr: RoleTrack, t, P, source: str) -> RoleTrack:
    obs = [Obs(t=float(a), point=[float(b[0]), float(b[1])]) for a, b in zip(t, P)]
    return RoleTrack(role=tr.role, object=tr.object, obs=obs, source=source)


def _resid(tq, Cq, t, P, fps):
    """Median residual of Qwen centres vs a trajectory after a constant offset, and coverage of Qwen's span."""
    if len(t) < 3:
        return math.inf, 0.0
    fr = np.round(t * fps).astype(int)
    frq = np.round(tq * fps).astype(int)
    common = [i for i, f in enumerate(frq) if f in set(fr)]
    cover = float(((tq >= t[0] - 0.5 / fps) & (tq <= t[-1] + 0.5 / fps)).mean())
    if len(common) < 3:
        return math.inf, cover
    pos = {f: i for i, f in enumerate(fr)}
    a = Cq[common]
    b = np.array([P[pos[frq[i]]] for i in common])
    off = np.median(a - b, axis=0)
    return float(np.median(np.linalg.norm(a - b - off, axis=1))), cover


def _valid(traj, fps, s):
    ok = np.isfinite(traj[:, 0])
    return np.nonzero(ok)[0] / fps, traj[ok] / s


def _border_drop(cen, boxes, shape):
    Hw, Ww = shape
    touch = (boxes[:, 0] <= 1) | (boxes[:, 1] <= 1) | (boxes[:, 2] >= Ww - 1) | (boxes[:, 3] >= Hw - 1)
    cen = cen.copy()
    cen[touch] = np.nan
    return cen


def twin_path(video_path: str) -> str | None:
    p = Path(video_path)
    if p.stem.endswith("_segmented"):
        return None
    q = p.with_name(p.stem + "_segmented" + p.suffix)
    return str(q) if q.exists() else None


def track_video(video_path: str, fps: float, tq, Cq, Sq, anchor_box, cache_key: str, split: str):
    """Candidate trajectories (original px) of the object in anchor_box: klt (+ halves), mask, seg.
    Returns dict name -> (t, P) and info."""
    cdir = CACHE / f"prior_{split}"
    cdir.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha1(json.dumps([video_path, round(fps, 4), [round(v, 1) for v in anchor_box],
                                   cache_key, 2]).encode()).hexdigest()[:16]
    cf = cdir / f"{Path(video_path).stem}_{key}.pkl"
    if cf.exists():
        return pickle.load(open(cf, "rb"))
    import cv2
    cv2.setNumThreads(1)
    out, info = {}, {}
    try:
        Gv, s = dyn.load_grey(video_path, None)
        if len(Gv) < 5:
            raise RuntimeError("no_frames")
        info["work_scale"] = s
        bg, share = dyn.background(Gv)
        info["static_share"] = share
        static = share <= dyn.STATIC_MAX
        fa = int(np.clip(round(tq[np.argmin(np.abs(tq - np.median(tq)))] * fps), 0, len(Gv) - 1))
        box_w = [v * s for v in anchor_box]
        pa_w = np.array([(box_w[0] + box_w[2]) / 2, (box_w[1] + box_w[3]) / 2])
        info["anchor_frame"] = fa
        fgs = (lambda f: dyn.fg_mask(Gv[f], bg)) if static else None
        klt, kinfo = dyn.klt_rigid(Gv, fa, box_w, fgs)
        if klt is not None:
            for k, v in klt.items():
                out[f"klt_{k}"] = _valid(v, fps, s)
        if static:
            m = dyn.mask_track(Gv, bg, fa, pa_w, box_w)
            if m is not None:
                out["mask"] = _valid(_border_drop(m["cen"], m["box"], Gv.shape[1:]), fps, s)
        segp = video_path if Path(video_path).stem.endswith("_segmented") else twin_path(video_path)
        if segp:
            if segp != video_path:
                Gs, ss = dyn.load_grey(segp, None)
                ok = len(Gs) == len(Gv) and Gs.shape[1:] == Gv.shape[1:]
            else:
                Gs, ss, ok = Gv, s, True
            if ok:
                bgs, _ = dyn.background(Gs)
                r = dyn.seg_track(Gs, bgs, fa, pa_w, box_w)
                if r is not None:
                    cen = _border_drop(r["cen"], r["box"], Gs.shape[1:])
                    cen[~r["valid"]] = np.nan
                    out["seg"] = _valid(cen, fps, ss)
                    info["seg_from"] = Path(segp).stem
    except Exception as e:  # noqa: BLE001
        info["error"] = f"{type(e).__name__}: {e}"
    res = (out, info)
    pickle.dump(res, open(cf, "wb"))
    return res


def iou(a, b):
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - ix * iy
    return ix * iy / u if u > 0 else 0.0


def cv_agreement(qobs, cvtr: RoleTrack | None, fps: float) -> float:
    if cvtr is None:
        return 0.0
    cb = {int(round(o.t * fps)): o.box for o in cvtr.obs if o.box is not None}
    vals = [iou(o.box, cb[int(round(o.t * fps))]) for o in qobs if o.box is not None and int(round(o.t * fps)) in cb]
    return float(np.median(vals)) if len(vals) >= 3 else 0.0


def candidates(split, video_path, fps, prior_tr: RoleTrack, cv_tr: RoleTrack | None, dense_tr: RoleTrack | None,
               do_track: bool = True):
    """name -> (RoleTrack, info) of the prior's candidate tracks (gated), for one question."""
    out, info = {"sparse": (prior_tr, {})}, {}
    t, C, S = _centres(prior_tr.obs)
    if len(t) < 3:
        return out, {"skip": "short"}
    inl = clean_mask(t, C, S)
    boxed = [o for o in prior_tr.obs if o.box is not None]
    boxed.sort(key=lambda o: o.t)
    clean_obs = [o for o, k in zip(boxed, inl) if k]
    info["clean_share"] = float(inl.mean())
    out["clean"] = (RoleTrack(role=prior_tr.role, object=prior_tr.object, obs=clean_obs, source="clean"), {})
    tq, Cq, Sq = t[inl], C[inl], S[inl]
    agree = cv_agreement(clean_obs, cv_tr, fps)
    info["cv_iou"] = agree
    if cv_tr is not None and agree >= IOU_MIN:
        out["cv"] = (cv_tr, {"iou": agree})
    if dense_tr is not None and any(o.point is not None for o in dense_tr.obs) and dense_tr.source == "dense":
        out["dense"] = (dense_tr, {})
    if not do_track:
        return out, info
    mid = int(np.argmin(np.abs(tq - np.median(tq))))
    anchor = [float(v) for v in clean_obs[mid].box]
    trajs, tinfo = track_video(video_path, fps, tq, Cq, Sq, anchor, prior_tr.object, split)
    info.update(tinfo)
    tol = max(6.0, 0.5 * float(np.median(Sq)))
    for name in ("klt", "mask", "seg"):
        k = "klt_all" if name == "klt" else name
        if k not in trajs:
            continue
        tt, P = trajs[k]
        res, cov = _resid(tq, Cq, tt, P, fps)
        info[f"{name}_resid"], info[f"{name}_cover"] = res, cov
        ok = res <= tol and cov >= COVER_MIN
        if ok:
            out[name] = (traj_track(prior_tr, tt, P, name), {"resid": res, "cover": cov})
    if "klt" in out and "klt_h0" in trajs and "klt_h1" in trajs:
        out["klt"][1]["halves"] = (trajs["klt_h0"], trajs["klt_h1"])
    return out, info


def measure_prior(spec, tracks, image_size, fps, prior_track: RoleTrack):
    """Re-solve with the prior track replaced -> (value, prior_px, flags)."""
    trs = [prior_track if tr.role == "prior" else tr for tr in tracks]
    ans = G.solve(spec, trs, image_size, fps)
    return ans.value, ans.debug.get("prior_px"), ans.flags


def halves_ok(spec, tracks, image_size, fps, prior_tr, halves) -> bool:
    vals = []
    for tt, P in halves:
        if len(tt) < 3:
            return False
        v, px, _ = measure_prior(spec, tracks, image_size, fps, traj_track(prior_tr, tt, P, "klt_half"))
        if not px:
            return False
        vals.append(px)
    return abs(math.log(vals[0] / vals[1])) <= HALVES_MAX


def choose(est: dict[str, float]) -> tuple[str | None, list[str]]:
    """est: candidate -> prior measurement. The largest group of candidates agreeing within AGREE (log) wins
    (ties: the group holding the highest-priority candidate); its highest-priority member is used. A lone
    candidate: the highest priority among seg, klt, mask, cv, dense; else clean."""
    names = [n for n in PRIORITY if n in est and est[n] and est[n] > 0]
    if not names:
        return None, []
    best = None
    for n in names:
        grp = [m for m in names if abs(math.log(est[m] / est[n])) <= AGREE]
        key = (len(grp), -min(PRIORITY.index(m) for m in grp))
        if best is None or key > best[0]:
            best = (key, grp)
    grp = sorted(best[1], key=PRIORITY.index)
    if len(grp) >= 2:
        return grp[0], grp
    return names[0], [names[0]]
