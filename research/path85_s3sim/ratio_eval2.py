"""(b) extended: focal-free ratio estimator = qp.geometry's prior-anchored solve restricted to rows whose TARGET has its
own depth_info entry (no target_depth_* fallback) and a prior with depth, any prior kind (size: f cancels; motion: lateral
speed / pixel speed sets m/px at the prior's range, f cancels to first order), size and speed targets.
Blends with Claude's direct log-median: gm (1/2), gm13 (1/3 geometry), gated by agreement."""
from common import *  # noqa

r = pd.read_csv(REPLAY)
fl = r.flags_old.fillna("")
r["own"] = r.kind.isin(["size", "speed"]) & (r.method_old == "3d_focal_from_prior") & \
    ~fl.str.contains("target_depth_|prior_depth|f_solve|default_focal|no_target|time_outside")
piv = lambda c: r.pivot_table(index="qid", columns="run", values=c, aggfunc="first")  # noqa: E731
T = pd.DataFrame({"dmed": lmed(piv("direct")), "geo": lmed(piv("geo_old").where(piv("own").astype(bool)))})
first = r.drop_duplicates("qid").set_index("qid")
T["video"], T["cat"], T["kind"], T["pk"] = first.video_id, first.category, first.kind, first.prior_kind
T["illc"] = piv("flags_old").apply(lambda s: s.fillna("").str.contains("f_ill|f_impl").mean() >= 0.5, axis=1)
T = T[T.geo.notna()]
T["gm"] = np.sqrt(T.dmed * T.geo)
T["gm13"] = T.dmed ** (2 / 3) * T.geo ** (1 / 3)
T["agree"] = np.where(np.abs(np.log(T.geo / T.dmed)) < 0.15, T.gm, T.dmed)
lv = val_labels(); lf, _ = fact_labels()
cols = ["dmed", "geo", "gm", "gm13", "agree"]
for name, lab in (("VALIDATION", lv), ("FACTS", lf)):
    x = T[T.index.isin(lab.index)].copy()
    x["lab"] = lab.reindex(x.index)
    S = pd.DataFrame({c: item_scores(x[c], x.lab) for c in cols}, index=x.index)
    print(f"== {name}: n={len(x)} clips={clip_cluster(x.video).nunique()}  " + "  ".join(f"{c} {S[c].mean():.3f}" for c in cols))
    for c in cols[1:]:
        print(f"     {c} - dmed {[round(v, 3) for v in boot_delta(S[c], S.dmed, clip_cluster(x.video))]}")
    for (k, pk), g in x.groupby(["kind", "pk"]):
        print(f"     {k} | prior {pk}: n={len(g)} " + "  ".join(f"{c} {S.loc[g.index, c].mean():.3f}" for c in cols))
    for ill, g in x.groupby(T.illc.reindex(x.index)):
        print(f"     f ill-conditioned={ill}: n={len(g)} " + "  ".join(f"{c} {S.loc[g.index, c].mean():.3f}" for c in cols))
print("test rows with an own-depth ratio estimate:", len(T), T.groupby(["cat", "kind"]).size().to_dict())
