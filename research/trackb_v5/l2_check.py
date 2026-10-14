"""L2 label-free check: on TEST S3 lab clips (size prior), the focal length that makes the open-track geometry
reproduce the STATED prior size vs the fixed lab camera f = 722 px at 1280 px (84 deg).
log(f_solved / f_cam) = log(stated / measured at f_cam) for a size measured as px * range / f."""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "trackb_dense"))
from solve import annotations  # noqa: E402
from tbcommon import questions  # noqa: E402
from qp import geometry as G  # noqa: E402

for src in sys.argv[1:] or ("qwen", "cvq"):
    df = questions("test")
    df = df[(df.video_source == "lab") & (df.category == "S3")]
    anns, paths, meta = annotations("test", src, df)
    got = {}
    orig = G._solve_f

    def wrap(fn, value, W, f_def):
        f = orig(fn, value, W, f_def)
        got["f"] = f
        return f
    G._solve_f = wrap
    rows = []
    try:
        for r in df.itertuples():
            a = anns.get(int(r.qid))
            if a is None or a.spec.prior.kind != "size":
                continue
            fps, (W, H), _ = meta[int(r.qid)]
            got.clear()
            G.solve(a.spec, a.tracks, (W, H), fps)
            f = got.get("f")
            if f:
                rows.append(dict(video=r.video_id, qid=r.qid, W=W, lr=math.log(f / (722.0 * W / 1280))))
    finally:
        G._solve_f = orig
    R = pd.DataFrame(rows)
    V = R.groupby("video").lr.median()
    print(f"{src}: {len(V)} S3 lab clips ({len(R)} q); per-clip log(f_solved/f_cam): median {V.median():+.3f}, "
          f"median |.| {V.abs().median():.3f}, IQR [{V.quantile(.25):+.3f}, {V.quantile(.75):+.3f}]; "
          f"implied FOV median {2*math.degrees(math.atan(640/(722*math.exp(V.median())))):.1f} deg")
