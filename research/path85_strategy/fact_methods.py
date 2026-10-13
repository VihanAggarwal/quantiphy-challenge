"""Label-free check: score the cached method variants on rows whose answer is an exact stated fact of the scene family
(facts / motionfam / freefall / labfacts rules applied to the raw run). Clustered by video."""
from common import *
t = pd.read_pickle(OUT / "table.pkl")
f = pd.read_csv(OUT / "facts_log.csv").drop_duplicates("qid").set_index("qid")
x = t.loc[f.index].copy(); x["fact"] = f.new
x["med3"] = np.exp(np.log(x[["d1", "d2", "d3"]]).median(axis=1, skipna=True))
x["gm"] = np.sqrt(x.r_geo_value * x.d1); x["gm_med3"] = np.sqrt(x.r_geo_value * x.med3)
x["raw"] = x.r_parsed_value
cols = ["raw", "r_geo_value", "d1", "gm", "med3", "gm_med3"]
for c in cols:
    ok = x[c].notna() & (x[c] > 0)
    x["s_" + c] = np.where(ok, item_scores(x[c].where(ok, 1.0), x.fact), np.nan)
    x["lr_" + c] = np.log(x[c] / x.fact)
pd.set_option("display.width", 250)
rows = []
for key, g in list(x.groupby("sub")) + list(x.groupby(x.category + ":" + x.srcg)):
    r = dict(sub=key, n=len(g), vids=g.video_id.nunique(), raw_route=(g.is_geo.mean()))
    for c in cols:
        r[c] = g["s_" + c].mean()
    for c in cols[1:]:
        gg = g[g["s_" + c].notna() & g.s_raw.notna()]
        if len(gg) >= 4:
            m, lo, hi = clustered_boot(gg["s_" + c] - gg.s_raw, gg.video_id)
            r[c + "_d"] = f"{m:+.3f} [{lo:+.3f},{hi:+.3f}]"
    r["med_lr_geo"] = g.lr_r_geo_value.median(); r["med_lr_d1"] = g.lr_d1.median()
    rows.append(r)
res = pd.DataFrame(rows)
print(res.round(3).to_string())
res.to_csv(OUT / "fact_methods.csv", index=False)
x.to_pickle(OUT / "facts_rows.pkl")
