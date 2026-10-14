"""Split-half held-out pseudo gain WITH the family rules: routing fitted on half A of the test fit videos (pseudo-labels),
applied to all rows, rules run, pseudo-MRA vs Track A scored on the scored rows of half B. Also the 28 val rows w/o Track A."""
import itertools, sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
exec(open(Path(__file__).parent / "eval_pl.py").read().split("# v3 + rules")[0])
from qp import postprocess as pp
C = pd.read_pickle(Path(__file__).parent / "cache.pkl")
v3post, plpost = C["v3post"], C["plpost"]
pl = rd(ROOT / "submissions/trackA_cand_combo2.csv")
# 28 unmatched val rows
key = {(v, pp.norm_question(q)) for v, q in zip(D.test.video_id, D.test.question)}
um = pd.Series([(v, pp.norm_question(q)) not in key for v, q in zip(D.val.video_id, D.val.question)], index=D.lab.index)
d = D.items(plpost) - D.items(v3post)
print("unmatched val rows by cat:", D.vcat[um].value_counts().to_dict(), "item sum change:", d[um].groupby(D.vcat[um]).sum().round(2).to_dict(),
      "videos:", D.vvid[um].unique().tolist())

fit = D.test[~D.test.video_id.isin(set(D.val.video_id))].copy()
fit["pl"] = fit.qid.map(pl).to_numpy(float)
def mra(p, g): return item_scores(np.where(np.isfinite(p) & (p > 0), p, 1e-9), g)
def lm(df, ms):
    L = np.log(np.vstack([D.P["test"][m].loc[df.index].to_numpy(float) for m in ms])); L[~np.isfinite(L)] = np.nan
    return np.exp(np.nanmedian(L, 0))
subs = [ms for k in (1, 2) for ms in itertools.combinations(MEM, k)]
subs3 = [ms for k in (1, 2, 3) for ms in itertools.combinations(MEM, k)]
S = pd.DataFrame({"+".join(k): mra(lm(fit, k), fit.pl.to_numpy()) for k in subs3}, index=fit.index)
scored = set(D.test.qid[~D.dup])
v3raw_v = D.raw(V3, "val")
vids = fit.video_id.unique(); rng = np.random.default_rng(7); res = []
for rep in range(8):
    A = set(rng.choice(vids, len(vids) // 2, replace=False))
    inA = fit.video_id.isin(A).to_numpy()
    fb, cs = {}, {}
    for c in CATS:
        mc = (fit.category == c).to_numpy()
        fb[c] = S.loc[mc & inA, ["+".join(m) for m in subs3]].mean().idxmax().split("+")
        for cell in fit.cell[mc].unique():
            mcell = mc & (fit.cell == cell).to_numpy()
            if (mcell & inA).sum() >= 13:
                cs[cell] = S.loc[mcell & inA, ["+".join(m) for m in subs]].mean().idxmax().split("+")
    rt, rv = raw_routed("test", cs, fb), raw_routed("val", cs, fb)
    post, _ = D.rules(combined_from_raw(rt, rv))
    B = fit[~inA & fit.qid.isin(scored)]
    g = pl.reindex(B.qid).to_numpy(float)
    r = {}
    for c in CATS:
        m = (B.category == c).to_numpy()
        r[c] = mra(post.reindex(B.qid).to_numpy(float)[m], g[m]).mean() - mra(v3post.reindex(B.qid).to_numpy(float)[m], g[m]).mean()
    r["macro"] = np.mean([r[c] for c in CATS])
    r["val_true"] = D.score(post)["MRA"] - D.score(v3post)["MRA"]
    res.append(r); print(rep, {k: round(v, 4) for k, v in r.items()}, flush=True)
R = pd.DataFrame(res); print("mean", R.mean().round(4).to_dict(), "sd", R.std().round(4).to_dict())
