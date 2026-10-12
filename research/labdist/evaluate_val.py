"""Validation check of the labdist family rules (labels used for EVALUATION only; nothing here sets a test answer).

Every validation lab clip is also a test clip, and its sibling renders (captured_X, Xs, Xx) are test clips whose
identical questions share the label. For each validation lab question this takes the probe-8 / raw / direct values of
the same question on all family renders in the TEST run and scores:
  own      the probe-8 value of the validation clip itself (what we submit there)
  R1       the original render's probe-8 value, where the clip is an s/x render answered by Claude's direct answer
  R2       the family log-median of probe-8 values, where the family spread exceeds 15%
Rows are all lab kinds (only 8 validation lab questions are distance-type, too few on their own).

    python research/labdist/evaluate_val.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from qp.mra import item_scores  # noqa: E402

BASE = ROOT / "submissions/trackA_probe8_p7b_d2fixes_d3labphys.csv"


def family(v):
    return re.sub(r"(captured_\d+[ab]?)[sxX]?$", r"\1", v)


def main():
    val = pd.read_csv(ROOT / "data/QuantiPhy-validation/validation_dataset.csv")
    t = pd.read_csv(ROOT / "data/submission_template/quantiphy_submission_template.csv")
    p8 = pd.read_csv(BASE).set_index("id").parsed_value
    raw = pd.read_csv(ROOT / "runs/test_v1_high_854/test.csv").set_index("id")
    t["p8"] = t.id.map(p8)
    t["direct"] = t.id.map(raw.direct_value)
    t["fam"] = t.video_id.map(family)
    t["qn"] = t.question.str.strip().str.lower()
    rows = []
    for _, r in val[val.video_source == "lab"].iterrows():
        g = t[(t.fam == family(r.video_id)) & (t.qn == r.question.strip().lower())]
        own = g[g.video_id == r.video_id]
        if not len(own):
            continue
        own = own.iloc[0]
        out = dict(video_id=r.video_id, question=r.question[:60], gt=r.ground_truth_posterior, own=own.p8, n=len(g))
        orig = g[g.video_id == own.fam]
        is_direct = np.isfinite(own.direct) and abs(own.p8 / own.direct - 1) < 1e-6
        out["R1"] = float(orig.p8.iloc[0]) if (own.video_id != own.fam and is_direct and len(orig)) else np.nan
        vals = g.p8.astype(float)
        out["R2"] = float(np.exp(np.median(np.log(vals)))) if (len(g) > 1 and vals.max() / vals.min() > 1.15) else np.nan
        rows.append(out)
    d = pd.DataFrame(rows)
    for c in ("own", "R1", "R2"):
        d["s_" + c] = item_scores(d[c].fillna(-1), d["gt"])
        d.loc[d[c].isna(), "s_" + c] = np.nan
    pd.set_option("display.width", 220)
    print(d.round(3).to_string(index=False))
    for c in ("R1", "R2"):
        m = d[c].notna()
        print(f"{c}: applies to {int(m.sum())} validation lab questions; own {d.loc[m, 's_own'].mean():.3f} -> "
              f"{c} {d.loc[m, 's_' + c].mean():.3f}")
    # the premise of R1 on raw Claude answers (before any probe rule): for validation s/x renders, the ORIGINAL
    # render's direct answer vs the clip's own direct answer, same question
    rows = []
    for _, r in val[(val.video_source == "lab") & (val.video_id.map(family) != val.video_id)].iterrows():
        g = t[(t.fam == family(r.video_id)) & (t.qn == r.question.strip().lower())]
        own, orig = g[g.video_id == r.video_id], g[g.video_id == family(r.video_id)]
        if len(own) and len(orig):
            rows.append(dict(gt=r.ground_truth_posterior, own=own.direct.iloc[0], orig=orig.direct.iloc[0]))
    e = pd.DataFrame(rows)
    so, sr = item_scores(e.own, e["gt"]), item_scores(e.orig, e["gt"])
    diff = sr - so
    rng = np.random.default_rng(0)
    boot = [rng.choice(diff, len(diff)).mean() for _ in range(4000)]
    print(f"R1 premise (raw direct answers, {len(e)} validation s/x lab questions): own {so.mean():.3f} -> original "
          f"render {sr.mean():.3f} (mean diff {diff.mean():+.3f}, 90% bootstrap [{np.percentile(boot, 5):+.3f}, "
          f"{np.percentile(boot, 95):+.3f}]; better {int((diff > 0).sum())}, worse {int((diff < 0).sum())})")


if __name__ == "__main__":
    main()
