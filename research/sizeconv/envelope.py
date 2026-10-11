"""Size envelope of articulated objects in 2D simulation clips (task A).

Labels for animals / people / flags are world axis-aligned boxes: the max extent over the animation (wingspan
= max in flight, people = T-pose height). The solver measures a size as the median of Claude's extent lines
(qp.geometry._Obj.lengths). For every size quantity (target or prior) about an articulated object this script
measures, along the image axis the extent runs on (horizontal / vertical; diagonal extents are skipped):
  cur      the solver's px length (median of the role track's extent lengths, else its box side)
  box_med  median over frames of Claude's box side (all tracks of that object in the clip's record)
  box_max  max over frames of Claude's box side
  m_med / m_p90 / m_max  the same from segmented-twin masks (clean, non-edge frames; cached features of
           research/levers_2026-10-11 twins/track_families.py)

    python research/sizeconv/envelope.py SPLIT OUT_CSV    (SPLIT = test | val_hires)
"""
from __future__ import annotations

import math
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import ROOT, is_artic, load  # noqa: E402
from qp.open.cv_track import object_key  # noqa: E402

import os  # noqa: E402
# twins/test_feats.pkl from research/levers_2026-10-11/levers_scripts_reports.tar.gz (extract it, set SIZECONV_FEATS)
FEATS = Path(os.environ.get("SIZECONV_FEATS", "/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/levers/twins/test_feats.pkl"))
NOT_ARTIC = ("cleaner", "tire", "tyre", "wheel", "vacuum", "boat", "car")
AXIS_TOL = 30.0     # deg: an extent within this of horizontal / vertical measures that image axis


def articulated(obj: str) -> bool:
    o = obj.lower()
    return is_artic(o) and not any(w in o for w in NOT_ARTIC)


def axis_of(track) -> tuple[str, float | None]:
    angs = []
    for o in track.obs:
        if o.extent is not None:
            (x0, y0), (x1, y1) = o.extent
            if math.hypot(x1 - x0, y1 - y0) >= 2:
                angs.append(math.degrees(math.atan2(y1 - y0, x1 - x0)) % 180.0)
    if not angs:
        return "none", None
    a = float(np.median(angs))
    d0 = min(a, 180 - a)
    if d0 <= AXIS_TOL:
        return "h", a
    if abs(a - 90) <= AXIS_TOL:
        return "v", a
    return "diag", a


def cur_px(track, dimension) -> float | None:
    L = [math.hypot(o.extent[1][0] - o.extent[0][0], o.extent[1][1] - o.extent[0][1]) for o in track.obs
         if o.extent is not None]
    L = [x for x in L if x > 0]
    if L:
        return float(np.median(L))
    d = (dimension or "").lower()
    B = [(o.box[2] - o.box[0], o.box[3] - o.box[1]) for o in track.obs if o.box is not None]
    if not B:
        return None
    if any(w in d for w in ("height", "tall", "vertical")):
        return float(np.median([h for _, h in B]))
    if any(w in d for w in ("width", "wide", "horizontal")):
        return float(np.median([w for w, _ in B]))
    return float(np.median([max(w, h) for w, h in B]))


def boxes_of(anns_vid, key) -> dict[float, list]:
    """{t: box} over all tracks of object `key` in one clip's annotations (Claude's boxes)."""
    out = {}
    for a in anns_vid:
        for tr in a.tracks:
            if object_key(tr.object)[0] != key:
                continue
            for o in tr.obs:
                if o.box is not None:
                    out.setdefault(round(o.t, 3), o.box)
    return out


def mask_sides(feats, vid, key):
    seg = vid if vid.endswith("_segmented") else vid + "_segmented"
    fam = feats.get(seg)
    if fam is None:
        return None
    fr = None
    for k in (f"test:{vid}|{key}", f"test:{seg}|{key}", f"val:{vid}|{key}"):
        if k in fam["feats"]:
            fr = fam["feats"][k]
            st = fam["stats"].get(k, {})
            break
    if fr is None:
        return None
    W, H = [], []
    for f in fr.values():
        if f.get("clean") and not f.get("edge"):
            x0, y0, x1, y1 = f["box"]
            W.append(x1 - x0)
            H.append(y1 - y0)
    if len(W) < 5:
        return None
    return np.array(W, float), np.array(H, float), len(fr)


def run(split: str) -> pd.DataFrame:
    df, anns, recs = load(split)
    feats = pickle.load(open(FEATS, "rb"))
    by_vid = {}
    for q, a in anns.items():
        if q in df.index:
            by_vid.setdefault(df.video_id[q], []).append(a)
    rows = []
    for q, r in df.iterrows():
        if not str(r.video_id).startswith("simulation") or str(r.category)[1] != "2" or q not in anns:
            continue
        a = anns[q]
        for role in ("target", "prior"):
            qq = getattr(a.spec, role)
            if qq.kind != "size" or not qq.objects or not articulated(" ".join(qq.objects)):
                continue
            tr = next((t for t in a.tracks if t.role == role), None)
            if tr is None or not tr.obs:
                # prior tracks are often empty after the first question of a clip: use any track of it
                tr = next((t for b in by_vid[r.video_id] for t in b.tracks
                           if t.role == role and object_key(t.object)[0] == object_key(qq.objects[0])[0] and t.obs
                           and getattr(b.spec, role).dimension == qq.dimension), None)
            if tr is None:
                continue
            key = object_key(tr.object)[0]
            ax, ang = axis_of(tr)
            c = cur_px(tr, qq.dimension)
            row = dict(qid=q, video_id=r.video_id, category=r.category, role=role, obj=tr.object, key=key,
                       dim=qq.dimension, axis=ax, angle=ang, cur=c, question=r.question, prior=r.prior)
            bx = boxes_of(by_vid[r.video_id], key)
            if bx and ax in ("h", "v"):
                s = np.array([(b[2] - b[0]) if ax == "h" else (b[3] - b[1]) for b in bx.values()], float)
                row.update(n_box=len(s), box_med=float(np.median(s)), box_max=float(s.max()))
            ms = mask_sides(feats, r.video_id, key)
            if ms is not None and ax in ("h", "v"):
                s = ms[0] if ax == "h" else ms[1]
                row.update(n_mask=len(s), m_med=float(np.median(s)), m_p90=float(np.percentile(s, 90)),
                           m_max=float(s.max()))
            rows.append(row)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    out = run(sys.argv[1])
    out.to_csv(sys.argv[2], index=False)
    for c in ("box_med", "box_max", "m_med", "m_p90", "m_max"):
        if c in out:
            out["r_" + c] = out[c] / out["cur"]
    pd.set_option("display.width", 250)
    print(out.groupby(["category", "role"]).size())
    print(out[[c for c in out if c.startswith("r_")]].describe().round(3))
