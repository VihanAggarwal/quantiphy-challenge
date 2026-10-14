"""L5: per-category member-set selection by validation, evaluated by leave-one-video-out WITH the family rules.

Family: every subset (size 1-5) of 8 methods. Each subset is applied to all categories, the trackb rules are run on
the combined table, item scores stored per validation row. Selection per category = best mean item on the training
videos; LOVO scores the held-out video. Compared with the same procedure restricted to the old 4 methods (how v3 was
picked) and with the fixed v3 sets (in-sample).
"""
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from harness import CATS, V3, Data  # noqa: E402

M8 = ["qwen_direct", "caw", "qwen_geo", "cv_geo", "cvq_geo", "qwen35", "gemma4", "qwen_fov"]
OLD4 = ["qwen_direct", "caw", "qwen_geo", "cv_geo"]
D = Data()
cache = HERE / "cache_l5_items.pkl"
I = pd.read_pickle(cache) if cache.exists() else {}
for k in range(1, 6):
    for ms in itertools.combinations(M8, k):
        key = "+".join(ms)
        if key in I:
            continue
        post, _ = D.rules(D.combined({c: list(ms) for c in CATS}))
        I[key] = D.items(post)
        if len(I) % 20 == 0:
            pd.to_pickle(I, cache)
            print(len(I), flush=True)
pd.to_pickle(I, cache)
I = pd.DataFrame(I)
cat, vid = D.vcat, D.vvid


def lovo(cols):
    held = pd.Series(np.nan, index=I.index)
    for c in CATS:
        mc = cat == c
        for v in vid[mc].unique():
            h = mc & (vid == v)
            tr = mc & (vid != v)
            best = I.loc[tr, cols].mean().idxmax()
            held[h] = I.loc[h, best]
    return {c: held[cat == c].mean() for c in CATS} | {"MRA": np.mean([held[cat == c].mean() for c in CATS])}


old_cols = [k for k in I.columns if all(m in OLD4 for m in k.split("+"))]
all_cols = list(I.columns)
v3post, _ = D.rules(D.combined(V3))
print("fixed v3 (in-sample)", D.score(v3post))
print("LOVO search old4 (v3's procedure)", {k: round(v, 4) for k, v in lovo(old_cols).items()})
print("LOVO search 8 methods", {k: round(v, 4) for k, v in lovo(all_cols).items()})
ins = {c: I.loc[cat == c].mean().idxmax() for c in CATS}
print("in-sample best per category (8 methods):", ins)
