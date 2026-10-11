"""Task B: lab size bias (ball motion blur) and depth convention, label-free on test via stated size priors.

For every lab clip whose prior is a stated size, the prior object is measured with the fixed lab camera
(f from qp.claude_annotate.LAB_FOV_DEG) and its depth_info entries, under four depth conventions:
  range   depth_info = Euclidean range to the object centre (the pipeline: Z = r / |ray|)
  zaxis   depth_info = optical-axis Z to the centre (Z = r)
  surf_r  range to the visible front surface (centre range = r + R for a ball of radius R)
  surf_z  optical-axis Z to the front surface (Z = r + R)
and compared with the stated value. Features: off-axis |ray|, R / r, the object's image speed in px per
frame relative to its px size (motion blur proxy) and whether it is a ball. The same is done for size
TARGETS on validation (labels used for evaluation only).

    python research/sizeconv/lab_sizes.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import ROOT, load  # noqa: E402
from qp import claude_annotate as ca  # noqa: E402
from qp import geometry as G  # noqa: E402
from qp.open.cv_track import is_sphere  # noqa: E402

OUT = ROOT / "research/sizeconv/out"


def f_cam(width: float, fov=ca.LAB_FOV_DEG) -> float:
    return width / 2 / math.tan(math.radians(fov) / 2)


def measure(q, track, spec, W, H, fps, value_si=None):
    """Per-convention measured size (m) of quantity q on `track`, plus features."""
    groups = G._depth_groups(spec.depth)
    if not groups:
        return None
    o = G._Obj(track, set())
    fn = G.match_depth([o.depth_name] if o.depth_name else [o.name, *q.objects], groups)
    if fn is None:
        fn = G.match_depth([o.name, *q.objects], groups)
    if fn is None:
        return None
    t, mid, L = o.lengths(q.dimension)
    if not len(L):
        return None
    f, c = f_cam(W), np.array([W / 2, H / 2])
    ray = np.column_stack([(mid - c) / f, np.ones(len(mid))])
    n = np.linalg.norm(ray, axis=1)
    r = np.asarray(fn(t), float)
    sphere = is_sphere(o.name) or is_sphere(" ".join(q.objects))
    R = (value_si / 2) if (sphere and value_si) else 0.0
    out = {"range": np.median(L * (r / n) / f), "zaxis": np.median(L * r / f),
           "surf_r": np.median(L * ((r + R) / n) / f), "surf_z": np.median(L * (r + R) / f)}
    # motion: px per frame of the object's reference point over its track (all obs), relative to its px size
    tp, uv = o.points()
    spd = np.nan
    if len(tp) >= 2:
        dt = np.diff(tp) * fps
        ok = dt > 0
        if ok.any():
            spd = float(np.median(np.linalg.norm(np.diff(uv, axis=0), axis=1)[ok] / dt[ok]))
    out.update(n_obs=len(L), len_px=float(np.median(L)), r=float(np.median(r)), offaxis=float(np.median(n)),
               R_over_r=R / float(np.median(r)) if R else 0.0, sphere=bool(sphere), px_per_frame=spd,
               blur=spd / float(np.median(L)) if np.isfinite(spd) else np.nan, depth_names="|".join(fn.names))
    return out


def run(split: str, role: str) -> pd.DataFrame:
    df, anns, recs = load(split)
    rows, seen = [], set()
    for qid, r in df.iterrows():
        if r.video_source != "lab" or qid not in anns:
            continue
        a = anns[qid]
        if not a.spec.is_3d:
            continue
        q = a.spec.prior if role == "prior" else a.spec.target
        if q.kind != "size":
            continue
        if role == "prior":
            key = (r.video_id, " ".join(q.objects), q.dimension)
            if key in seen:
                continue
        tr = next((t for t in a.tracks if t.role == role and t.obs), None)
        if tr is None:
            continue
        m = recs[r.video_id]["meta"]
        W, H = m["image_size"]
        stated = q.value_si if role == "prior" else None
        res = measure(q, tr, a.spec, W, H, float(m["fps"]), value_si=stated)
        if res is None:
            continue
        if role == "prior":
            seen.add(key)
        rows.append(dict(qid=qid, video_id=r.video_id, category=r.category, obj=tr.object, dim=q.dimension,
                         stated=stated, question=r.question, prior=r.prior, unit=r.target_unit, **res))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 300)
    tp = run("test", "prior"); tp.to_csv(OUT / "lab_priors_test.csv", index=False)
    vp = run("val_hires", "prior"); vp.to_csv(OUT / "lab_priors_val.csv", index=False)
    vt = run("val_hires", "target"); vt.to_csv(OUT / "lab_targets_val.csv", index=False)
    tt = run("test", "target"); tt.to_csv(OUT / "lab_targets_test.csv", index=False)
    for name, d in (("test priors", tp), ("val priors", vp)):
        for cv in ("range", "zaxis", "surf_r", "surf_z"):
            d["lr_" + cv] = np.log(d[cv] / d.stated)
        print(name, len(d))
        print(d.groupby("sphere")[[c for c in d if c.startswith("lr_")]].agg(["median", "mean", "count"]).round(3))
