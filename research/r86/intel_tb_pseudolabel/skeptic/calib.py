"""(1) On validation rows: pseudo-delta (vs Track A combo2 answers of the duplicated test rows) vs true delta.
(2) Split-half on test videos: fit routing on half A (pseudo-labels), evaluate pseudo-MRA on half B (raw, no rules)."""
import itertools, sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
exec(open(Path(__file__).parent / "eval_pl.py").read().split("# v3 + rules")[0])
from qp import postprocess as pp
C = pd.read_pickle(Path(__file__).parent / "cache.pkl")
v3post, plpost = C["v3post"], C["plpost"]
pl = rd(ROOT / "submissions/trackA_cand_combo2.csv")
# map val rows -> duplicated test qids
key = {(v, pp.norm_question(q)): qid for v, q, qid in zip(D.test.video_id, D.test.question, D.test.qid)}
vmap = pd.Series([key.get((v, pp.norm_question(q))) for v, q in zip(D.val.video_id, D.val.question)],
                 index=D.val.qid.to_numpy() + VAL_OFFSET)
print("val rows with a Track A answer:", vmap.notna().sum(), "of", len(vmap))
ta = pl.reindex(vmap.dropna().astype(int)).set_axis(vmap.dropna().index)
idx = ta.index
lab = D.lab.reindex(idx)
def it(p, g): return pd.Series(item_scores(p.reindex(idx).to_numpy(float), g.to_numpy(float)), index=idx)
cat = D.vcat.reindex(idx)
print("Track A true MRA on these val rows:", {c: round(it(ta, lab)[cat == c].mean(), 3) for c in CATS})
for nm, a, b in (("after rules", v3post, plpost),):
    tv3, tpl = it(a, lab), it(b, lab)
    pv3, ppl = it(a, ta), it(b, ta)
    for c in CATS:
        m = cat == c
        print(f"{nm} {c}: true {tv3[m].mean():.3f}->{tpl[m].mean():.3f} ({tpl[m].mean()-tv3[m].mean():+.3f}) | pseudo {pv3[m].mean():.3f}->{ppl[m].mean():.3f} ({ppl[m].mean()-pv3[m].mean():+.3f})")
    dt = np.mean([tpl[cat == c].mean() - tv3[cat == c].mean() for c in CATS])
    dp = np.mean([ppl[cat == c].mean() - pv3[cat == c].mean() for c in CATS])
    print(f"{nm} macro: true delta {dt:+.4f} | pseudo delta {dp:+.4f}")

# (2) split-half on test fit videos (raw, no rules), 10 random splits
fit = D.test[~D.test.video_id.isin(set(D.val.video_id))].copy()
fit["pl"] = fit.qid.map(pl).to_numpy(float)
P = {m: D.P["test"][m] for m in MEM}
def lm(df, ms):
    L = np.log(np.vstack([P[m].loc[df.index].to_numpy(float) for m in ms])); L[~np.isfinite(L)] = np.nan
    return np.exp(np.nanmedian(L, 0))
def mra(p, g): return item_scores(np.where(np.isfinite(p) & (p > 0), p, 1e-9), g)
subs = [ms for k in (1, 2) for ms in itertools.combinations(MEM, k)]
subs3 = [ms for k in (1, 2, 3) for ms in itertools.combinations(MEM, k)]
# precompute per-row item scores vs pseudo-labels for every subset
S = {ms: mra(lm(fit, ms), fit.pl.to_numpy()) for ms in subs3}
S = pd.DataFrame({"+".join(k): v for k, v in S.items()}, index=fit.index)
v3k = {c: "+".join(V3[c]) for c in CATS}
for c in CATS:
    if v3k[c] not in S:
        S[v3k[c]] = mra(lm(fit, V3[c]), fit.pl.to_numpy())
vids = fit.video_id.unique(); rng = np.random.default_rng(1)
res = []
for rep in range(20):
    A = set(rng.choice(vids, len(vids) // 2, replace=False))
    inA = fit.video_id.isin(A).to_numpy()
    out_ins, out_ho, base_ho, base_ins = [], [], [], []
    for c in CATS:
        mc = (fit.category == c).to_numpy()
        # fallback: best k<=3 category set on half A
        fbk = S.loc[mc & inA, ["+".join(m) for m in subs3]].mean().idxmax()
        chosen = pd.Series(fbk, index=fit.index[mc])
        for cell in fit.cell[mc].unique():
            mcell = mc & (fit.cell == cell).to_numpy()
            if (mcell & inA).sum() < 25 * 0.5:  # half the data -> half the threshold
                continue
            chosen[fit.index[mcell]] = S.loc[mcell & inA, ["+".join(m) for m in subs]].mean().idxmax()
        sc = np.array([S.at[i, k] for i, k in chosen.items()])
        hb = ~inA[mc]
        out_ho.append(sc[hb].mean()); out_ins.append(sc[~hb].mean())
        base_ho.append(S.loc[mc & ~inA, v3k[c]].mean()); base_ins.append(S.loc[mc & inA, v3k[c]].mean())
    res.append(dict(ins=np.mean(out_ins) - np.mean(base_ins), ho=np.mean(out_ho) - np.mean(base_ho),
                    **{f"ho_{c}": o - b for c, o, b in zip(CATS, out_ho, base_ho)}))
R = pd.DataFrame(res)
print("split-half pseudo gain over v3 sets (raw): in-sample", round(R.ins.mean(), 4), "| held-out", round(R.ho.mean(), 4),
      "sd", round(R.ho.std(), 4), {c: round(R[f"ho_{c}"].mean(), 3) for c in CATS})
