"""Validation (EVALUATION ONLY): video-bootstrap CIs for re-ask gains on flagged subsets, lab direct medians,
and geometry/direct routing inside flagged subsets.

    .venv/bin/python research/reask/val_boot.py   (after val_eval.py)
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp.mra import item_scores  # noqa: E402

r = pd.read_csv(Path(__file__).with_name("val_rows.csv")).set_index("qid")
rng = np.random.default_rng(0)
vids = r.video_id.unique()


def boot(mask, a, b, B=4000):
    """sum over flagged rows of (a - b) per video, bootstrap over videos; returns mean gain/row and 90% CI."""
    d = (r[a] - r[b]).where(mask, np.nan)
    per = pd.DataFrame({"s": d.fillna(0), "n": mask.astype(int), "v": r.video_id}).groupby("v").sum()
    per = per.reindex(vids).fillna(0)
    est = per.s.sum() / max(per.n.sum(), 1)
    k = rng.integers(0, len(vids), size=(B, len(vids)))
    sv, nv = per.s.to_numpy()[k].sum(1), per.n.to_numpy()[k].sum(1)
    lo, hi = np.percentile(sv / np.maximum(nv, 1), [5, 95])
    return est, lo, hi, int(mask.sum())


def col(run, split, c):
    return pd.read_csv(ROOT / run / f"{split}.csv").set_index("id")[c].reindex(r.index)


# direct-answer medians (what the 3D non-lab ensemble does) incl. 4th/5th members
D = pd.DataFrame({"base": r.direct_value, "v1b": col("runs/val_opus_high", "val", "direct_value"),
                  "v2": col("runs/val_hr_v2_high", "val_hires", "direct_value"),
                  "med": col("runs/val_opus_med", "val", "direct_value"),
                  "med2": col("runs/val_opus_med2", "val", "direct_value"),
                  "fable": col("runs/val_fable_high", "val", "direct_value"),
                  "xhigh": col("runs/val_opus_xhigh", "val", "direct_value"),
                  "v2b": col("runs/val_v2_high", "val", "direct_value")})
gm = lambda cols: np.exp(np.log(D[cols].where(D[cols] > 0)).median(axis=1, skipna=True))  # noqa: E731
S = lambda p: item_scores(p.fillna(r.parsed_value), r.answer)  # noqa: E731
r["d_base"] = S(D.base)
r["d_med3"] = S(gm(["base", "v1b", "v2"]))
r["d_med4"] = S(gm(["base", "v1b", "v2", "v2b"]))
r["d_med5"] = S(gm(["base", "v1b", "v2", "v2b", "xhigh"]))
r["d_med5m"] = S(gm(["base", "v1b", "v2", "med", "med2"]))
r["geo"] = S(r.geo_value)
# a re-ask that returns a fresh v1-high-like sample: the parsed answer of val_opus_high
r["reask1"] = r["v1b"]

conf = r.conf <= 0.3
out = []
for src in ["ALL", "2D", "lab", "3Dnl"]:
    g = pd.Series(True, index=r.index) if src == "ALL" else (r.src == src)
    for fname, f in {"all": g, "conf<=0.3": g & conf, "conf<=0.2": g & (r.conf <= 0.2),
                     "gd>0.2": g & (r.gd > 0.2), "direct": g & (r.method == "direct"),
                     "dspread3>0.15": g & (r.dspread3 > 0.15)}.items():
        if f.sum() < 3:
            continue
        for a, b in [("reask1", "base"), ("med3", "base"), ("med5", "base"), ("verify_final", "base"),
                     ("d_med3", "d_base"), ("d_med5", "d_base"), ("d_med5m", "d_base"), ("d_med4", "d_med3"),
                     ("d_med5", "d_med3"), ("geo", "base")]:
            e, lo, hi, n = boot(f, a, b)
            out.append(dict(src=src, flag=fname, n=n, comp=f"{a}-{b}", gain=e, lo=lo, hi=hi))
res = pd.DataFrame(out)
pd.set_option("display.width", 200)
print(res.round(3).to_string(index=False))
res.to_csv(Path(__file__).with_name("val_boot_table.csv"), index=False)
