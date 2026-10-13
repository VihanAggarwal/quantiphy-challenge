"""3D non-lab: which aggregate of the 3 cached direct runs is best? (facts = label-free; validation overlap = eval only)
median (base rule) vs geometric mean vs mean-of-closest-two vs run1. Clustered by video."""
from common import *
t = pd.read_pickle(OUT / "table.pkl")
f = pd.read_csv(OUT / "facts_log.csv").drop_duplicates("qid").set_index("qid")
t["fact"] = f.new.reindex(t.index)
L = np.log(t[["d1", "d2", "d3"]].where(t[["d1", "d2", "d3"]] > 0))
t["med3"] = np.exp(L.median(axis=1)); t["gm3"] = np.exp(L.mean(axis=1))
def close2(r):
    a = np.sort(r.dropna().to_numpy())
    if len(a) < 3: return np.exp(a.mean()) if len(a) else np.nan
    return np.exp(a[:2].mean()) if a[1] - a[0] <= a[2] - a[1] else np.exp(a[1:].mean())
t["cl2"] = [close2(L.loc[q]) for q in t.index]
t["spread"] = L.max(axis=1) - L.min(axis=1)
nl = t[(t.srcg == "sim") & t.category.isin(["S3", "D3"]) & t.d2.notna()]
for lab, sel in (("facts", nl.fact.notna()), ("val", nl.overlap & nl.val.notna())):
    x = nl[sel].copy(); y = x.fact if lab == "facts" else x.val
    for c in ("d1", "med3", "gm3", "cl2"):
        x["s_" + c] = item_scores(x[c], y)
    print(lab, len(x), x.video_id.nunique(), {c: round(x["s_" + c].mean(), 4) for c in ("d1", "med3", "gm3", "cl2")})
    for c in ("gm3", "cl2"):
        print("  ", c, "- med3", [round(v, 4) for v in clustered_boot(x["s_" + c] - x.s_med3, x.video_id)])
    hi = x.spread > 0.15
    print("   spread>0.15 rows", int(hi.sum()), {c: round(x.loc[hi, "s_" + c].mean(), 4) for c in ("d1", "med3", "gm3", "cl2")})
# how many submitted rows are pure med3 (aggregator switch would touch them)
pure = nl[np.isclose(nl.base, nl.med3, rtol=1e-6) & ~nl.overlap]
print("pure-median scored rows:", pure.category.value_counts().to_dict(), " |gm3/med3-1|>5%:", int((np.abs(np.log(pure.gm3 / pure.med3)) > 0.05).sum()))
