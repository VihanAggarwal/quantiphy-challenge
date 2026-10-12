"""Per-category median-set selection over the Track B methods (old four + the new geometry variants), with a
leave-one-video-out (LOVO) estimate of the selection itself.

    .venv/bin/python research/trackb_dense/select_sets.py [--methods a,b,...] [--max-size 5]

Every method is a full answer set on val and test: the four Colab methods (trackb_v1) and the geometry variants of
out/<split>/<tag>.csv with run_open_vlm's direct fallback (CaW; geometry beyond loose bounds or > 10x off CaW is
replaced). For each category the member set (any subset of the methods up to --max-size members) whose per-question
log-median scores best on validation is chosen; LOVO repeats that choice without each validation video and scores
the held-out video. Writes out/sets.json (the in-sample choice per category) and prints the table.
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
from evaluate import geo_method  # noqa: E402
from tbcommon import CATS, OUT, base_preds, item, log_median, questions  # noqa: E402

V3 = {"S2": ["caw", "cv_geo", "qwen_direct"], "D2": ["caw", "cv_geo", "qwen_direct", "qwen_geo"],
      "S3": ["cv_geo", "qwen_geo", "qwen_direct"], "D3": ["caw", "qwen_geo", "qwen_direct"]}
NEW = {"val": {"qwen_dense": "qwen_dense_labfov", "qwen_dyn": "qwen_dyn", "hybrid": "hybrid_mean_labfov",
               "hybrid_nopick": "hybrid_nopick_labfov", "cv_labfov": "cv_labfov",
               "qwen_labfov": "qwen_sparse_labfov"},
       "test": {"qwen_dense": "qwen_dense_labfov", "qwen_dyn": "qwen_dyn", "hybrid": "hybrid_mean_labfov",
                "hybrid_nopick": "hybrid_nopick_labfov", "cv_labfov": "cv_labfov",
                "qwen_labfov": "qwen_sparse_labfov"}}


def all_methods(split: str, df: pd.DataFrame, names=None) -> dict[str, pd.Series]:
    P = base_preds(split, df.qid)
    for m, tag in NEW[split].items():
        if names and m not in names:
            continue
        if (OUT / split / f"{tag}.csv").exists():
            P[m] = geo_method(split, tag, df, P["caw"])
    return {m: p.reindex(df.qid).set_axis(df.index) for m, p in P.items() if not names or m in names}


def subsets(methods, max_size):
    for k in range(1, max_size + 1):
        yield from itertools.combinations(methods, k)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--methods", default="")
    ap.add_argument("--max-size", type=int, default=5)
    ap.add_argument("--out", default="sets.json")
    a = ap.parse_args(argv)
    names = [m for m in a.methods.split(",") if m] or None
    val = questions("val")
    P = all_methods("val", val, names)
    methods = list(P)
    print("methods:", methods)
    S = {}
    for ms in subsets(methods, a.max_size):
        S[ms] = item(log_median([P[m] for m in ms]), val.answer)
    I = pd.DataFrame({"+".join(k): v for k, v in S.items()})
    vid = val.video_id
    res, choice = {}, {}
    for c in CATS:
        mc = (val.category == c).to_numpy()
        Ic = I[mc]
        best = Ic.mean().idxmax()
        choice[c] = best.split("+")
        held = pd.Series(np.nan, index=Ic.index)
        for v in vid[mc].unique():
            h = (vid[mc] == v).to_numpy()
            b = Ic[~h].mean().idxmax()
            held[h] = Ic.loc[h, b]
        v3 = "+".join(sorted(V3[c], key=methods.index)) if all(m in methods for m in V3[c]) else None
        res[c] = dict(lovo=held.mean(), insample=Ic[best].mean(), v3=Ic[v3].mean() if v3 else np.nan,
                      n=int(mc.sum()))
        print(f"{c}: in-sample best {best} {Ic[best].mean():.3f}; LOVO {held.mean():.3f}; v3 set "
              f"{res[c]['v3']:.3f}; single best {max((Ic[m].mean(), m) for m in methods)}")
    R = pd.DataFrame(res).T
    print(R.round(4).to_string())
    print(f"macro: LOVO {R.lovo.mean():.4f}  in-sample {R.insample.mean():.4f}  v3 sets {R.v3.mean():.4f}")
    json.dump(choice, open(OUT / a.out, "w"), indent=1)
    return choice, R


if __name__ == "__main__":
    main()
