"""Fact-based bias per subset with FAMILY-clustered bootstrap (a family's cameras share one scene and one error)."""
from common import *
x = pd.read_pickle(OUT / "facts_rows.pkl")
fam = pd.read_csv(OUT / "families.csv").set_index("video_id")
x["fam"] = fam.famm.reindex(x.video_id).to_numpy()
x["use"] = np.where(x.srcg == "sim", np.where(x.category.str.endswith("3"), x.med3, x.r_geo_value), x.raw)
x = x[x.use.notna() & (x.use > 0)]
x["lr"] = np.log(x.use / x.fact)
rng = np.random.default_rng(1)
for key, g in list(x.groupby("sub")):
    if len(g) < 6: continue
    fams = g.fam.unique(); by = {f: g.lr[g.fam == f].to_numpy() for f in fams}
    meds = [np.median(np.concatenate([by[f] for f in rng.choice(fams, len(fams))])) for _ in range(2000)]
    gain = {k: item_scores(g.use * k, g.fact).mean() - item_scores(g.use, g.fact).mean() for k in (0.95, 1.035, 1.05)}
    # family-clustered CI of the k=1.035 / 0.95 gain
    d = pd.Series(item_scores(g.use * 1.035, g.fact) - item_scores(g.use, g.fact), index=g.index)
    m, lo, hi = clustered_boot(d, g.fam)
    print(f"{key:14s} n={len(g):3d} fams={len(fams):2d} med_lr={g.lr.median():+.3f} famCI=[{np.quantile(meds,.05):+.3f},{np.quantile(meds,.95):+.3f}]"
          f" gain k1.035 {m:+.3f} [{lo:+.3f},{hi:+.3f}]  " + " ".join(f"k{k}:{v:+.3f}" for k, v in gain.items()))
