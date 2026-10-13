"""(a) Per-subset method choice: for every category x source x kind subset, the rows that still hold the raw pipeline
answer (switchable), the label-free (stated facts) and validation (eval only) per-row gain of each alternative vs the
current method, and the implied overall gain of the best alternative = gain * n_scored_switchable / (4 * N_cat).
Facts and validation are pooled (row-weighted) for the estimate; CIs are video-clustered."""
from common import *
t = pd.read_pickle(OUT / "table.pkl")
f = pd.read_csv(OUT / "facts_log.csv").drop_duplicates("qid").set_index("qid")
t["fact"] = f.new.reindex(t.index)
L = np.log(t[["d1", "d2", "d3"]].where(t[["d1", "d2", "d3"]] > 0))
t["med3"] = np.exp(L.median(axis=1))
t["cur"] = np.where((t.srcg == "sim") & t.category.str.endswith("3") & t.med3.notna(), t.med3, t.r_parsed_value)
t["geo"] = t.r_geo_value; t["dir"] = np.where(t.med3.notna(), t.med3, t.d1); t["gm"] = np.sqrt(t.geo * t.dir)
t["label"] = t.fact.fillna(t.val)
t["src_lab"] = np.where(t.fact.notna(), "fact", np.where(t.val.notna(), "val", ""))
t["subk"] = t.category + ":" + t.srcg + ":" + np.where(t.motion, "mot", "stat")
# current method per subset (the routing): 2D geometry, 3D non-lab direct(med3), lab static geometry, lab motion direct
rows = []
for k, g in t.groupby("subk"):
    sw = g[g.raw_in_base & ~g.overlap & g.geo.notna() & (g.geo > 0) & g.dir.notna() & (g.dir > 0)]
    lab = g[g.label.notna() & (g.geo > 0) & (g.dir > 0) & g.cur.notna()]
    r = dict(subset=k, n_scored=int((~g.overlap).sum()), switchable=len(sw), n_lab=len(lab), vids=lab.video_id.nunique(),
             cur_route=("geo" if (g.is_geo.mean() > .5) else "direct"))
    if len(lab) >= 4:
        sc = {m: item_scores(lab[m], lab.label) for m in ("cur", "geo", "dir", "gm")}
        best, bg = None, -9
        for m in ("geo", "dir", "gm"):
            d = pd.Series(sc[m] - sc["cur"], index=lab.index)
            mm, lo, hi = clustered_boot(d, lab.video_id)
            r[m] = f"{mm:+.3f} [{lo:+.3f},{hi:+.3f}]"
            if mm > bg: best, bg = m, mm
        r["best_alt"] = best; r["gain_row"] = bg
        r["overall_if_switched"] = bg * len(sw) / (4 * N_SCORED[k[:2]])
    rows.append(r)
res = pd.DataFrame(rows)
pd.set_option("display.width", 250)
print(res.round(4).to_string())
pos = res[res.overall_if_switched > 0]
print("sum of positive per-subset switches (point estimates):", round(pos.overall_if_switched.sum(), 4))
res.to_csv(OUT / "subset_choice.csv", index=False)
