"""(c) per-kind systematic bias of Claude's direct answers (log-median of 3 runs) on 3D simulation rows, measured on
exact stated facts (label-free) and validation (evaluation only). Clip-clustered bootstrap of the median/mean log ratio."""
from common import *  # noqa

tab = pd.read_csv(ROOT / "research/simfov/out/table.csv").set_index("qid")
test = test_df().set_index("qid")
lv = val_labels(); lf, flog = fact_labels()
rows = []
for name, lab in (("val", lv), ("fact", lf)):
    x = tab[tab.index.isin(lab.index)].copy()
    x["lab"] = lab.reindex(x.index); x["src"] = name
    rows.append(x)
X = pd.concat(rows)
X["lr"] = np.log(X.dmed / X.lab)
X["clp"] = clip_cluster(X.video_id)
X["prior_kind"] = X.prior_kind.fillna("?")
def summ(g):
    rng = np.random.default_rng(0)
    cl = g.clp.unique()
    bs = []
    for _ in range(1000):
        k = rng.choice(cl, len(cl))
        bs.append(np.concatenate([g.lr[g.clp == c].to_numpy() for c in k]).mean())
    return pd.Series(dict(n=len(g), clips=len(cl), mean_lr=g.lr.mean(), med_lr=g.lr.median(),
                          lo=np.percentile(bs, 5), hi=np.percentile(bs, 95), mra=item_scores(g.dmed, g.lab).mean(),
                          mra_x=np.nan))
pd.set_option("display.width", 200)
print(X.groupby(["src", "category", "kind"]).apply(summ).round(3))
print(X.groupby(["src", "prior_kind", "kind"]).apply(summ).round(3))
X.to_csv(Path(__file__).with_name("out_bias_rows.csv"))
