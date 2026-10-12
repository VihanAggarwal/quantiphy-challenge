"""Re-solve lab distance-type questions (distance / displacement / path_length) with qp.geometry under depth and
focal conventions, on the cached Claude tracks (no API). Writes out/resolve_<split>.csv.

    python research/labdist/resolve.py test|val_hires
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "research/sizeconv"))
from common import load  # noqa: E402  (sizeconv loader: questions, annotations, records)
from qp import claude_annotate as ca  # noqa: E402
from qp import geometry as G  # noqa: E402

KINDS = ("distance", "displacement", "path_length")
VARIANTS = {            # name: (DEPTH_IS_RANGE, horizontal FOV deg)
    "range84": (True, ca.LAB_FOV_DEG),
    "z84": (False, ca.LAB_FOV_DEG),
    "range80": (True, 80.0),
    "z80": (False, 80.0),
}


def main(split):
    df, anns, recs = load(split)
    rows = []
    for qid, r in df.iterrows():
        if r.video_source != "lab" or qid not in anns or not anns[qid].spec.is_3d:
            continue
        a = anns[qid]
        if a.spec.target.kind not in KINDS:
            continue
        m = recs[r.video_id]["meta"]
        out = dict(id=qid, video_id=r.video_id, kind=a.spec.target.kind, question=r.question)
        for name, (rng, fov) in VARIANTS.items():
            G.DEPTH_IS_RANGE = rng
            ans = G.solve(a.spec, a.tracks, tuple(m["image_size"]), float(m["fps"]),
                          seen_scale=float(m.get("scale") or 1.0), camera_fov_deg=fov)
            out[name] = ans.value
            if name == "range84":
                out["flags"] = ";".join(sorted(ans.flags or []))
                out["method"] = ans.method
                out["f_px"] = (ans.debug or {}).get("f_px")
                out["depths"] = "|".join(f"{k}={v}" for k, v in (ans.debug or {}).items() if k.startswith(("depth_", "range_")))
        G.DEPTH_IS_RANGE = True
        rows.append(out)
    d = pd.DataFrame(rows)
    d.to_csv(HERE / f"out/resolve_{split}.csv", index=False)
    print(d.drop(columns=["question"]).round(3).to_string())


if __name__ == "__main__":
    (HERE / "out").mkdir(exist_ok=True)
    main(sys.argv[1])
