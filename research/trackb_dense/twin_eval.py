"""Label-free check of the prior-motion candidates on TEST: the segmented twin's foreground mask as reference.

For a clip X whose pixel-aligned re-render X_segmented exists, the "seg" candidate of X is the prior object's mask
centroid tracked on the white-background twin (dyn.seg_track), independent of the trackers being compared (only the
anchor box comes from Qwen). Per question: |log(candidate prior measurement / seg)| for each other candidate and
for the choice made without seg. Also: X vs X_segmented consistency of the chosen measurement (same pixels).

    .venv/bin/python research/trackb_dense/twin_eval.py [split]
"""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prior_motion as PM  # noqa: E402
from tbcommon import OUT  # noqa: E402

split = sys.argv[1] if len(sys.argv) > 1 else "test"
R = pd.read_csv(OUT / split / "prior_cands.csv")
px = [c for c in R.columns if c.startswith("px_")]
names = [c[3:] for c in px]


def pick_wo_seg(r):
    est = {n: r[f"px_{n}"] for n in names if n not in ("seg", "sparse") and np.isfinite(r[f"px_{n}"])}
    p, _ = PM.choose(est)
    return r[f"px_{p}"] if p else np.nan


R["px_pick_noseg"] = R.apply(pick_wo_seg, axis=1)
orig = R[~R.video_id.str.endswith("_segmented") & R.px_seg.notna()]
# one row per video (median over its questions: they share the prior)
V = orig.groupby("video_id")[[c for c in R.columns if c.startswith("px_")]].median()
rows = []
for c in V.columns:
    if c == "px_seg":
        continue
    e = np.abs(np.log(V[c] / V.px_seg))
    ok = np.isfinite(e)
    rows.append(dict(cand=c[3:], n=int(ok.sum()), median=e[ok].median(), mean=e[ok].mean(),
                     within5=(e[ok] < .05).mean(), over20=(e[ok] > .2).mean(), over50=(e[ok] > np.log(1.5)).mean()))
T = pd.DataFrame(rows).set_index("cand")
print(f"{split}: {len(V)} original clips with a twin-mask reference")
print(T.round(3).to_string())
# X vs X_segmented consistency of the chosen measurement
P = R.groupby("video_id")[["px_sparse", "px_dense", "px_clean"]].median()
P["pick"] = R.assign(pv=[getattr(r, f"px_{r.pick}") if isinstance(r.pick, str) else np.nan for r in R.itertuples()]
                     ).groupby("video_id").pv.median()
segs = [v for v in P.index if v.endswith("_segmented") and v[:-10] in P.index]
if not segs:
    sys.exit(0)
for c in P.columns:
    e = np.abs(np.log(P.loc[segs, c].to_numpy() / P.loc[[v[:-10] for v in segs], c].to_numpy()))
    e = e[np.isfinite(e)]
    print(f"twin consistency {c:10s} pairs {len(e)} median |log| {np.median(e):.3f} over20% {(e > .2).mean():.2f}")
