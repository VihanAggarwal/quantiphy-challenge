"""Per-family table of lab distance-type questions (distance / displacement / path_length) on test.

Renders of one lab event (captured_X, X s, X x: same pixels in the object regions, same depth_info) share their
labels, so every render's measurement is a sample of one label. For each question this re-solves qp.geometry
(unchanged code) with
  geo_any   the render's own tracks, distance axis forced to "any" (3D Euclidean, the label's convention for
            lab distances: hand-clicked points back-projected with the ToF depth)
  geo_orig  the original render's tracks for the same question (pixel-identical objects), axis "any"
and lists probe 8, the raw pipeline and Claude's direct answer. Writes out/family_table.csv.

    python research/labdist/family_table.py
"""
from __future__ import annotations

import copy
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research/sizeconv"))
from common import load  # noqa: E402
from qp import claude_annotate as ca  # noqa: E402
from qp import geometry as G  # noqa: E402

KINDS = ("distance", "displacement", "path_length", "camera_distance")
BASE = ROOT / "submissions/trackA_probe8_p7b_d2fixes_d3labphys.csv"


def family(v):
    return re.sub(r"(captured_\d+[ab]?)[sxX]?$", r"\1", v)


def solve(a, meta, axis_any=True, tracks=None):
    spec = copy.deepcopy(a.spec)
    if axis_any:
        spec.target.axis = "any"
    ans = G.solve(spec, tracks if tracks is not None else a.tracks, tuple(meta["image_size"]), float(meta["fps"]),
                  seen_scale=float(meta.get("scale") or 1.0), camera_fov_deg=ca.LAB_FOV_DEG)
    return ans


def main():
    df, anns, recs = load("test")
    p8 = pd.read_csv(BASE).set_index("id").parsed_value
    raw = pd.read_csv(ROOT / "runs/test_v1_high_854/test.csv").set_index("id")
    val = pd.read_csv(ROOT / "data/QuantiPhy-validation/validation_dataset.csv")
    overlap = set(zip(val.video_id, val.question.str.strip()))
    lab = df[(df.video_source == "lab")].copy()
    lab["fam"] = lab.video_id.map(family)
    lab["qnorm"] = lab.question.str.strip().str.lower()
    rows = []
    for qid, r in lab.iterrows():
        a = anns.get(qid)
        if a is None or a.spec.target.kind not in KINDS:
            continue
        m = recs[r.video_id]["meta"]
        out = dict(id=qid, video_id=r.video_id, fam=r.fam, category=r.category, kind=a.spec.target.kind,
                   axis=a.spec.target.axis, t=a.spec.target.time, objs="|".join(a.spec.target.objects),
                   question=r.question, overlap=(r.video_id, r.question.strip()) in overlap,
                   p8=float(p8[qid]), raw=float(raw.loc[qid, "parsed_value"]), direct=raw.loc[qid, "direct_value"],
                   method=raw.loc[qid, "method"])
        ans = solve(a, m)
        out["geo_any"] = ans.value
        out["geo_flags"] = ";".join(sorted(ans.flags))
        # the original render's tracks for the same question text
        sib = lab[(lab.video_id == r.fam) & (lab.qnorm == r.qnorm)]
        out["geo_orig"] = np.nan
        if len(sib) and r.video_id != r.fam:
            sa = anns.get(sib.index[0])
            if sa is not None and sa.tracks:
                out["geo_orig"] = solve(a, m, tracks=sa.tracks).value
        rows.append(out)
    d = pd.DataFrame(rows).sort_values("id")
    d.to_csv(HERE / "out/family_table.csv", index=False)
    pd.set_option("display.width", 260)
    pd.set_option("display.max_rows", 400)
    print(d[["id", "video_id", "category", "kind", "axis", "t", "objs", "overlap", "p8", "raw", "direct", "geo_any",
             "geo_orig"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
