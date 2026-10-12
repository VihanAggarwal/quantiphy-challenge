"""Leave-one-video-out comparison of member-set SELECTION PROCEDURES (less freedom = less overfitting).

    .venv/bin/python research/trackb_dense/lovo_procs.py [--methods a,b,...]

Procedures (each re-run without the held-out video, scored on it):
  fixed:<name>     a set fixed in advance (v3 sets; all methods)
  topk:K           per category, the median of the K methods with the best validation MRA in that category
  topk:auto        K (1..7) chosen per category inside the fold
  topk2d3d:K       ranking pooled over 2D (S2+D2) / 3D (S3+D3) instead of per category
  search<=N        exhaustive per-category subset search up to N members (v3's procedure)
Prints the LOVO macro MRA per procedure and the in-fold choice made on all videos.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from select_sets import V3, all_methods  # noqa: E402
from tbcommon import CATS, OUT, item, log_median, questions  # noqa: E402

GROUP = {"S2": ("S2", "D2"), "D2": ("S2", "D2"), "S3": ("S3", "D3"), "D3": ("S3", "D3")}


class Scorer:
    def __init__(self, P, val):
        self.P, self.val, self.cache = P, val, {}

    def items(self, ms):
        ms = tuple(sorted(ms))
        if ms not in self.cache:
            self.cache[ms] = item(log_median([self.P[m] for m in ms]), self.val.answer).to_numpy()
        return self.cache[ms]


def cat_mean(x, mask_rows, cats):
    return float(np.mean([x[mask_rows & (cats == c)].mean() for c in np.unique(cats[mask_rows])]))


def procedure(name, S: Scorer, methods, train, cats):
    """-> {category: member list} chosen on rows `train`."""
    single = {m: S.items((m,)) for m in methods}
    out = {}
    for c in CATS:
        if name.startswith("fixed:"):
            out[c] = FIXED[name[6:]][c]
            continue
        if name.startswith("topk2d3d:"):
            grp = train & np.isin(cats, GROUP[c])
            rank = sorted(methods, key=lambda m: -cat_mean(single[m], grp, cats))
            out[c] = rank[:int(name.split(":")[1])]
            continue
        rows = train & (cats == c)
        rank = sorted(methods, key=lambda m: -single[m][rows].mean())
        if name.startswith("topk:"):
            k = name.split(":")[1]
            if k == "auto":
                best = max(range(1, min(7, len(rank)) + 1), key=lambda kk: S.items(rank[:kk])[rows].mean())
                out[c] = rank[:best]
            else:
                out[c] = rank[:int(k)]
        elif name.startswith("search<="):
            n = int(name[8:])
            subs = [s for k in range(1, n + 1) for s in itertools.combinations(methods, k)]
            out[c] = list(max(subs, key=lambda s: S.items(s)[rows].mean()))
    return out


def evaluate(name, S, methods, val):
    cats = val.category.to_numpy()
    vids = val.video_id.to_numpy()
    held = np.full(len(val), np.nan)
    for v in np.unique(vids):
        h = vids == v
        ch = procedure(name, S, methods, ~h, cats)
        for c in CATS:
            r = h & (cats == c)
            if r.any():
                held[r] = S.items(ch[c])[r]
    full = procedure(name, S, methods, np.ones(len(val), bool), cats)
    ins = np.full(len(val), np.nan)
    for c in CATS:
        ins[cats == c] = S.items(full[c])[cats == c]
    per = {c: held[cats == c].mean() for c in CATS}
    return dict(proc=name, LOVO=np.mean(list(per.values())), **{f"lovo_{c}": per[c] for c in CATS},
                insample=np.mean([ins[cats == c].mean() for c in CATS])), full


FIXED = {"v3": V3}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--methods", default="")
    ap.add_argument("--procs", default="fixed:v3,fixed:all,topk:2,topk:3,topk:4,topk:5,topk:auto,topk2d3d:3,"
                                         "topk2d3d:4,topk2d3d:5,search<=3")
    ap.add_argument("--out", default="lovo_procs.json")
    a = ap.parse_args(argv)
    val = questions("val")
    names = [m for m in a.methods.split(",") if m] or None
    P = all_methods("val", val, names)
    methods = list(P)
    FIXED["all"] = {c: methods for c in CATS}
    S = Scorer(P, val)
    rows, choices = [], {}
    for name in a.procs.split(","):
        r, full = evaluate(name, S, methods, val)
        rows.append(r)
        choices[name] = full
        print(f"{name:14s} LOVO {r['LOVO']:.4f} (" + " ".join(f"{c} {r['lovo_' + c]:.3f}" for c in CATS)
              + f")  in-sample {r['insample']:.4f}", flush=True)
    json.dump({"methods": methods, "choices": choices, "rows": rows}, open(OUT / a.out, "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
