"""Hybrid Qwen + SAM 2 geometry: per role, the SAM 2 (cv) track where it agrees with Qwen's boxes, else Qwen's.

    .venv/bin/python research/trackb_dense/hybrid.py val|test [--lab-fov] [--size mean|cv|qwen] [--tag NAME]

Per question and role (prior, prior2, target, target2):
  * prior of a 2D motion prior: the track run_prior.py chose (prior_tracks_<split>.pkl; its candidates include the
    cv track when it agrees with Qwen), else as below;
  * cv agrees (median IoU of the boxes at common frames >= IOU_MIN): motion quantities take the cv track (per-frame
    SAM 2 mask centroids); sizes take the log-mean of the two extents (--size mean: both sources measure the same
    object, independent box errors) or one source;
  * otherwise Qwen's track after qp.dense_track (the qwen_dense annotations).
Writes out/<split>/<tag>.csv (solve.py format).
"""
from __future__ import annotations

import argparse
import math
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prior_motion import IOU_MIN, iou  # noqa: E402
from tbcommon import CACHE, OUT, questions, tracks  # noqa: E402
from qp import combine  # noqa: E402
from qp.claude_annotate import LAB_FOV_DEG  # noqa: E402
from qp.geometry import solve  # noqa: E402
from qp.spec import RoleTrack  # noqa: E402
from solve import annotations  # noqa: E402

SIZE_KINDS = ("size", "other")


def agreement(a: RoleTrack, b: RoleTrack, fps: float) -> float:
    bb = {int(round(o.t * fps)): o.box for o in b.obs if o.box is not None}
    v = [iou(o.box, bb[int(round(o.t * fps))]) for o in a.obs if o.box is not None and int(round(o.t * fps)) in bb]
    return float(np.median(v)) if len(v) >= 2 else 0.0


def scaled_boxes(tr: RoleTrack, k: float) -> RoleTrack:
    """Track with every box scaled about its centre by k (size sources combined by a log-mean)."""
    obs = []
    for o in tr.obs:
        if o.box is not None:
            cx, cy = (o.box[0] + o.box[2]) / 2, (o.box[1] + o.box[3]) / 2
            w, h = (o.box[2] - o.box[0]) * k / 2, (o.box[3] - o.box[1]) * k / 2
            o = type(o)(**{**o.__dict__, "box": [cx - w, cy - h, cx + w, cy + h], "extent": None})
        obs.append(o)
    return RoleTrack(role=tr.role, object=tr.object, obs=obs, source=tr.source)


def side(tr: RoleTrack, dim: str) -> float:
    from qp.geometry import _Obj
    t, mid, L = _Obj(tr, set()).lengths(dim)
    return float(np.median(L)) if len(L) else math.nan


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("split")
    ap.add_argument("--lab-fov", action="store_true")
    ap.add_argument("--size", default="mean", choices=["mean", "cv", "qwen"])
    ap.add_argument("--no-prior-pick", action="store_true")
    ap.add_argument("--tag", default="")
    ap.add_argument("--cv-src", default="cvq", help="SAM 2 source: cvq (prompted by Qwen's boxes) or cv")
    a = ap.parse_args(argv)
    df = questions(a.split)
    _, _, meta = annotations(a.split, "qwen", df)
    dtag = "qwen_dense" if a.split == "val" else "qwen_dense_labfov"
    dense = pickle.load(open(CACHE / f"anns_{a.split}_{dtag}.pkl", "rb"))
    picks = {} if a.no_prior_pick else pickle.load(open(CACHE / f"prior_tracks_{a.split}.pkl", "rb"))
    cvrec = tracks(a.split, a.cv_src)
    rows, used = [], []
    for r in df.itertuples():
        q = int(r.qid)
        row = dict(id=q, geo_value=np.nan, geo_si=np.nan, flags="no_tracks", method="", prior_px=np.nan,
                   target_px=np.nan)
        if q not in dense:
            rows.append(row)
            continue
        ann = dense[q]
        fps, size, _ = meta[q]
        cv = {}
        rec = cvrec.get(r.video_id)
        if rec and str(q) in rec.get("tracks", {}):
            cv = {t["role"]: RoleTrack.from_dict(t) for t in rec["tracks"][str(q)]}
        new = []
        for tr in ann.tracks:
            qty = ann.spec.prior if tr.role.startswith("prior") else ann.spec.target
            if tr.role == "prior" and picks.get(q) is not None:
                new.append(picks[q])
                used.append("pick")
                continue
            c = cv.get(tr.role)
            ag = agreement(tr, c, fps) if c is not None else 0.0
            if c is None or ag < IOU_MIN:
                new.append(tr)
                used.append("qwen")
                continue
            if qty.kind in SIZE_KINDS:
                if a.size == "cv":
                    new.append(c)
                elif a.size == "qwen":
                    new.append(tr)
                else:
                    sq, sc = side(tr, qty.dimension), side(c, qty.dimension)
                    new.append(scaled_boxes(tr, math.sqrt(sc / sq)) if sq > 0 and sc > 0 else tr)
                used.append(f"size_{a.size}")
            else:
                new.append(c)
                used.append("cv_motion")
        fov = LAB_FOV_DEG if a.lab_fov and r.video_source in combine.CAMERA_SOURCES and ann.spec.is_3d else None
        ans = solve(ann.spec, new, size, fps, **({"camera_fov_deg": fov} if fov else {}))
        row.update(geo_value=ans.value if ans.value else np.nan, geo_si=ans.debug.get("value_si", np.nan),
                   flags=";".join(ans.flags), method=ans.method or "", prior_px=ans.debug.get("prior_px", np.nan),
                   target_px=ans.debug.get("target_px", np.nan))
        rows.append(row)
    tag = a.tag or f"hybrid_{a.cv_src}_{a.size}{'_nopick' if a.no_prior_pick else ''}{'_labfov' if a.lab_fov else ''}"
    pd.DataFrame(rows).to_csv(OUT / a.split / f"{tag}.csv", index=False)
    print(tag, pd.Series(used).value_counts().to_dict())


if __name__ == "__main__":
    main()
