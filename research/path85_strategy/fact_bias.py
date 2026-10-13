"""Label-free bias check: on exact stated-fact rows, the raw answer that the submission would use without the fact
(3D sim: median of 3 direct runs; 2D: geometry; lab: run answer). Median log ratio with a video-clustered CI and the
MRA of a uniform multiplier k (score(k*x) - score(x)) per subset."""
from common import *
x = pd.read_pickle(OUT / "facts_rows.pkl")
x["use"] = np.where(x.srcg == "sim", np.where(x.category.str.endswith("3"), x.med3, x.r_geo_value), x.raw)
x = x[x.use.notna() & (x.use > 0)]
x["lr"] = np.log(x.use / x.fact)
rng = np.random.default_rng(0)
def boot_median(g, n=2000):
    vids = g.video_id.unique(); by = {v: g.lr[g.video_id == v].to_numpy() for v in vids}
    out = []
    for _ in range(n):
        s = rng.choice(vids, len(vids)); out.append(np.median(np.concatenate([by[v] for v in s])))
    return np.quantile(out, [.05, .95])
ks = [0.90, 0.93, 0.95, 0.97, 1.03, 1.05, 1.07, 1.10]
rows = []
grp = list(x.groupby("sub")) + list(x.groupby(x.category + ":" + x.srcg + ":" + x.kind))
for key, g in grp:
    if len(g) < 6: continue
    lo, hi = boot_median(g)
    r = dict(sub=key, n=len(g), vids=g.video_id.nunique(), med_lr=g.lr.median(), ci=f"[{lo:+.3f},{hi:+.3f}]",
             mad=np.median(np.abs(g.lr - g.lr.median())), base=item_scores(g.use, g.fact).mean())
    for k in ks:
        r[f"k{k}"] = item_scores(g.use * k, g.fact).mean() - r["base"]
    rows.append(r)
pd.set_option("display.width", 250)
print(pd.DataFrame(rows).round(3).to_string())
