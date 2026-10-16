"""Expected item-point change of the internet candidate vs the current best, under label hypotheses.

For each changed row: truth T = X * exp(N(0, sig^2)), X = 'new' value, 'base' value (C1_solS2S3, the leaderboard-tested
physical scale with the pipeline's planar measurement), or 'old' (agent in-clip: the adverse hypothesis).
R2 rows (exact stated facts): X = the stated value.
    .venv/bin/python research/next/inet/expected.py
"""
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "/home/user/quantiphy-challenge")
from qp.mra import item_scores  # noqa: E402

L = pd.read_csv("/home/user/quantiphy-challenge/research/next/inet/log_changes.csv")
rng = np.random.default_rng(0)
N_D2, N_S2 = 1090, 530   # approx scored rows on the new 3,010-row set (old 1137 / 553 scaled by 3010/3161)


def e(pred, x, sig, n=4000):
    g = x[None, :] * np.exp(rng.normal(0, sig, (n, len(x))))
    return np.array([item_scores(pred, gi) for gi in g]).mean(axis=0)


rows = []
for sig in (0.05, 0.10, 0.15):
    for hyp in ("new", "base", "old"):
        x = L[hyp].to_numpy(float).copy()
        fact = L.rule.eq("R2").to_numpy()
        x[fact] = L.new[fact]
        d = e(L.new.to_numpy(float), x, sig) - e(L.old.to_numpy(float), x, sig)
        L["d"] = d
        g = L.groupby(["rule", "category"]).d.sum()
        rows.append(dict(sig=sig, truth=hyp, **{f"{a}/{b}": round(v, 2) for (a, b), v in g.items()},
                         D2_pts=round(L.d[L.category.eq("D2")].sum(), 2), S2_pts=round(L.d[L.category.eq("S2")].sum(), 2),
                         D2=round(L.d[L.category.eq("D2")].sum() / N_D2, 4), S2=round(L.d[L.category.eq("S2")].sum() / N_S2, 4)))
pd.set_option("display.width", 250)
print(pd.DataFrame(rows).to_string(index=False))
# per clip at sig .10, truth = base and truth = new
for hyp in ("new", "base"):
    x = L[hyp].to_numpy(float).copy()
    x[L.rule.eq("R2").to_numpy()] = L.new[L.rule.eq("R2")]
    L["d"] = e(L.new.to_numpy(float), x, 0.10) - e(L.old.to_numpy(float), x, 0.10)
    print(hyp, L.groupby("video_id").d.sum().round(2).to_dict())
