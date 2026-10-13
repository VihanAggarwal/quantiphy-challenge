"""(b) size-from-depth ratio estimator  S_T = S_P * (px_T * r_T) / (px_P * r_P)  == qp.geometry's 3d_focal_from_prior
solve for a size prior with depth and a size target with its OWN depth entry (no target_depth_* fallback flag).
Replayed geometry from research/simfov/out/replay.csv (3 cached Claude runs, no API). Scored on validation
(identical test questions; evaluation only) and exact stated facts (label-free)."""
from common import *  # noqa

r = pd.read_csv(REPLAY)
r["own"] = (r.kind == "size") & (r.prior_kind == "size") & (r.method_old == "3d_focal_from_prior") & \
    ~r.flags_old.fillna("").str.contains("target_depth_|f_ill|f_impl|f_solve|default_focal|prior_depth")
piv = lambda c: r.pivot_table(index="qid", columns="run", values=c, aggfunc="first")  # noqa: E731
T = pd.DataFrame({"dmed": lmed(piv("direct")), "old": lmed(piv("geo_old").where(piv("own").astype(bool)))})
first = r.drop_duplicates("qid").set_index("qid")
T["video"], T["cat"], T["kind"] = first.video_id, first.category, first.kind
T["own_n"] = piv("own").sum(axis=1)
T["sens"] = piv("sens_old").median(axis=1)
sub = read_sub()
T["cur"] = sub.reindex(T.index)
T["gm"] = np.sqrt(T.dmed * T.old)
T["gm13"] = T.dmed ** (2 / 3) * T.old ** (1 / 3)
lv = val_labels(); lf, _ = fact_labels()
for name, lab in (("VALIDATION", lv), ("FACTS", lf)):
    x = T[T.index.isin(lab.index) & T.old.notna()].copy()
    x["lab"] = lab.reindex(x.index)
    print(f"\n== {name}: own-depth size rows with ratio estimate: n={len(x)}, clips={clip_cluster(x.video).nunique()}")
    S = pd.DataFrame({c: item_scores(x[c], x.lab) for c in ("dmed", "old", "gm", "gm13", "cur")}, index=x.index)
    print(S.mean().round(3).to_dict())
    print("by cat", S.groupby(x.cat).mean().round(3).to_dict("index"))
    for c in ("old", "gm", "gm13"):
        print(c, "- dmed", [round(v, 3) for v in boot_delta(S[c], S.dmed, clip_cluster(x.video))])
    E = pd.DataFrame({c: np.log(x[c] / x.lab) for c in ("dmed", "old")})
    print("median log err", E.median().round(3).to_dict(), "| median |log err|", E.abs().median().round(3).to_dict())
    print("corr of log errors dmed vs old:", round(E.corr().iloc[0, 1], 3))
    # sensitivity gate
    for lo in (0.5, 0.8):
        m = x.sens >= lo
        if m.sum():
            print(f"  sens>={lo}: n={m.sum()} dmed {S.dmed[m].mean():.3f} old {S.old[m].mean():.3f} gm {S.gm[m].mean():.3f}")
print("\ntest rows with an own-depth ratio estimate:", T.old.notna().sum(), T[T.old.notna()].groupby("cat").size().to_dict())
T.to_csv(Path(__file__).with_name("out_ratio_table.csv"))
