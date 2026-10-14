"""Bucket loss map: subset x kind, test scored row counts, estimated item mean, loss in overall points.
Subset means = leaderboard-decoded (p21 diagE/F) + category deltas since p21 allocated to the subsets whose rows changed.
Within-subset split: (E1) validation kind effects, shrunk; (E2) disagreement proxy calibrated on labelled rows.
Fact rows (final = stated value) assumed .97. Analysis only."""
import numpy as np, pandas as pd
from pathlib import Path
OUT = Path(__file__).parent
t = pd.read_pickle(OUT / "master.pkl")
NC = {"S2": 553, "D2": 1137, "S3": 538, "D3": 933}
dec = {"S2:sim+seg": .828, "S2:internet": .796, "D2:sim-static": .851, "D2:rest": .857,
       "S3:sim+seg": .742, "S3:lab": .782, "D3:lab-static": .799, "D3:rest": .805}
# category-point deltas p21 -> combo3 (scored combo2 + U-read expectations), allocated by changed rows
dcat = {"S2:sim+seg": .015, "S2:internet": .002, "D2:sim-static": .002, "D2:rest": .008,
        "S3:sim+seg": 0, "S3:lab": .004, "D3:lab-static": .001, "D3:rest": .010}
s = t[t.scored].copy()
ns = s.groupby("subset").size()
m3 = {k: dec[k] + dcat[k] * NC[k[:2]] / ns[k] for k in dec}
s["isfact"] = s.prov == "fact"
FACT = .97
# E2 proxy: E[score | disagreement] from labelled rows (val final + facts raw)
lab = pd.concat([t[t.val.notna()].assign(score=t.sc_val), t[t.fact.notna()].assign(score=t.sc_fact_raw)])
sim3 = lambda d: d.category.isin(["S3", "D3"]) & (d.srcg == "sim")
def bins(d):
    b = pd.Series("na", index=d.index)
    b[~sim3(d)] = pd.cut(d.dgd[~sim3(d)], [-1, .05, .15, .4, 1e9], labels=["g<5", "g5-15", "g15-40", "g>40"]).astype(str)
    b[sim3(d)] = pd.cut(d.spread[sim3(d)].fillna(0), [-1, .05, .15, 1e9], labels=["s<5", "s5-15", "s>15"]).astype(str)
    return b
lab["bin"] = bins(lab); s["bin"] = bins(s)
cal = lab.groupby("bin").score.mean()
s["proxy"] = s.bin.map(cal).fillna(lab.score.mean())
# E1: validation kind effect within subset (in-sample, shrunk n/(n+8))
v = t[t.val.notna()]
vk = v.groupby(["subset", "kg"]).sc_val.agg(["mean", "size"])
vs = v.groupby("subset").sc_val.mean()
rows = []
for sub, g in s.groupby("subset"):
    nf = (~g.isfact).sum(); target_nf = (m3[sub] * len(g) - FACT * g.isfact.sum()) / nf
    # E2: shift proxy so that the non-fact mean equals target_nf
    pr = g.proxy[~g.isfact]; sh = target_nf - pr.mean()
    for kg, h in g.groupby("kg"):
        hn = h[~h.isfact]
        e2 = (hn.proxy + sh).mean() if len(hn) else np.nan
        if (sub, kg) in vk.index:
            mu, n = vk.loc[(sub, kg)]; eff = (mu - vs[sub]) * n / (n + 8)
        else:
            mu, n, eff = np.nan, 0, 0.0
        rows.append(dict(subset=sub, kind=kg, n=len(h), fact=int(h.isfact.sum()), nonfact=len(hn),
                         rule=int(hn.prov.str.startswith("rule").sum()), e1_raw=target_nf + eff, e2=e2,
                         val_n=int(n), val_mean=mu, target_nf=target_nf))
b = pd.DataFrame(rows)
# re-centre E1 so the subset's non-fact total matches
for sub, g in b.groupby("subset"):
    tot = (g.e1_raw * g.nonfact).sum() / g.nonfact.sum()
    b.loc[g.index, "e1"] = g.e1_raw - (tot - g.target_nf.iloc[0])
b["est"] = (b.e1 + b.e2) / 2
b["est_all"] = (b.est * b.nonfact + FACT * b.fact) / b.n
b["w"] = [1 / (4 * NC[x[:2]]) for x in b.subset]
b["loss_pts"] = b.n * (1 - b.est_all) * b.w
b["pts_per_row_per_.10"] = b.w * .10
print({k: round(v, 3) for k, v in m3.items()})
print("total loss", round(b.loss_pts.sum(), 4))
pd.set_option("display.width", 200)
print(b[["subset", "kind", "n", "fact", "rule", "val_n", "val_mean", "e1", "e2", "est_all", "loss_pts"]]
      .sort_values("loss_pts", ascending=False).round(3).to_string(index=False))
b.to_csv(OUT / "buckets.csv", index=False)
print(cal.round(3).to_dict())
