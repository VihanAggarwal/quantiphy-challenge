"""Task B, depth convention: re-solve every lab 3D question with depth_info read as Euclidean range to the
object (the pipeline, qp.geometry.DEPTH_IS_RANGE = True) and as optical-axis Z (False), on the same tracks and
the same lab camera prior; ratio Z / range per question. Validation: score both on the lab rows whose pipeline
answer is geometry (labels for evaluation only). qp/geometry.py is not edited: the flag is set at runtime.

    python research/sizeconv/lab_depthconv.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import RAW, ROOT, load, read_csv  # noqa: E402
from qp import claude_annotate as ca  # noqa: E402
from qp import geometry as G  # noqa: E402
from qp.mra import item_scores  # noqa: E402


def solve_all(split):
    df, anns, recs = load(split)
    out = {}
    for qid, r in df.iterrows():
        if r.video_source != "lab" or qid not in anns or not anns[qid].spec.is_3d:
            continue
        a, m = anns[qid], recs[r.video_id]["meta"]
        vals = []
        for flag in (True, False):
            G.DEPTH_IS_RANGE = flag
            ans = G.solve(a.spec, a.tracks, tuple(m["image_size"]), float(m["fps"]),
                          seen_scale=float(m.get("scale") or 1.0), camera_fov_deg=ca.LAB_FOV_DEG)
            vals.append(ans.value)
        G.DEPTH_IS_RANGE = True
        out[qid] = dict(kind=a.spec.target.kind, range=vals[0], zaxis=vals[1])
    return df, pd.DataFrame(out).T


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    from qp.data import load_validation
    df, s = solve_all("val_hires")
    gt = load_validation().set_index("qid")
    raw = pd.read_csv(RAW["val_hires"]).set_index("id")
    s = s.join(raw[["parsed_value", "method"]])
    s = s[s.method.str.startswith("geometry") & s.range.notna() & s.zaxis.notna()]
    s["ratio"] = s.zaxis.astype(float) / s.range.astype(float)
    s["pipe_z"] = s.parsed_value * s.ratio
    s["gt"] = gt.answer.reindex(s.index)
    s["s_range"] = item_scores(s.parsed_value, s["gt"])
    s["s_z"] = item_scores(s.pipe_z, s["gt"])
    print("VAL lab geometry rows", len(s))
    print(s.groupby("kind")[["s_range", "s_z", "ratio"]].agg(["mean", "count"]).round(3))
    print(s[["kind", "gt", "parsed_value", "pipe_z", "ratio", "s_range", "s_z"]].round(3).to_string())
    dft, st = solve_all("test")
    st["ratio"] = st.zaxis.astype(float) / st.range.astype(float)
    st.to_csv(ROOT / "research/sizeconv/out/lab_depthconv_test.csv")
    print("TEST lab: Z/range ratio by kind")
    print(st.groupby("kind")["ratio"].describe().round(3))
