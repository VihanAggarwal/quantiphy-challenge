"""LOFO of the per-clip scale K (fact-based) variants on 3D sim facts: a held-out fact row is predicted by its raw
direct answer x exp(K), K from the clip's OTHER facts (different stated line).  Variants: median({0} U l) (current),
median(l), mean(l), shrunk mean n/(n+1), plus consensus-augmented: median({0} U l U kcons-terms)."""
from common import *  # noqa

tab = pd.read_csv(ROOT / "research/simfov/out/table.csv").set_index("qid")
raw = tab.dmed
lf, flog = fact_labels(raw)
flog = flog.set_index(flog.qid.astype(int))
test = test_df().set_index("qid")
rows = []
for q in lf.index:
    if q not in raw.index or tab.kind[q] not in ("size", "speed"):
        continue
    v = test.video_id[q]
    line = flog.loc[q, "reason"] if q in flog.index else ""
    others = [p for p in lf.index if p != q and p in raw.index and test.video_id[p] == v and
              tab.kind[p] in ("size", "speed") and flog.loc[p, "reason"] != line]
    ls = np.array([np.log(lf[p] / raw[p]) for p in others])
    rec = dict(qid=q, video=v, cat=test.category[q], kind=tab.kind[q], n=len(ls), raw=raw[q], lab=lf[q])
    rec["K0med"] = np.median(np.r_[0.0, ls]) if len(ls) else 0.0
    rec["Kmed"] = np.median(ls) if len(ls) else 0.0
    rec["Kmean"] = ls.mean() if len(ls) else 0.0
    rec["Kshr"] = ls.mean() * len(ls) / (len(ls) + 1) if len(ls) else 0.0
    rows.append(rec)
R = pd.DataFrame(rows)
cols = ["K0med", "Kmed", "Kmean", "Kshr"]
for c in cols:
    R[c + "_p"] = R.raw * np.exp(R[c])
for cat, g in R.groupby("cat"):
    g1 = g[g.n > 0]
    S = pd.DataFrame({c: item_scores(g1[c if c == "raw" else c + "_p"], g1.lab) for c in ["raw"] + cols}, index=g1.index)
    print(f"{cat}: rows with >=1 other fact n={len(g1)} clips={clip_cluster(g1.video).nunique()}  " +
          "  ".join(f"{c} {S[c].mean():.3f}" for c in S.columns))
    for c in cols[1:]:
        print(f"   {c} - K0med {[round(x, 3) for x in boot_delta(S[c], S.K0med, clip_cluster(g1.video))]}")
    for k, gk in g1.groupby("kind"):
        print(f"   kind {k} n={len(gk)}: " + "  ".join(f"{c} {S.loc[gk.index, c].mean():.3f}" for c in S.columns))
