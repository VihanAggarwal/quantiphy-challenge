"""Expected effect of trackA_cand_next_accounting.csv on the NEW scored set (H1 of scored_set.py), per category.
F rows: gain = 1 - item(agent, stated) if the stated sibling value is the label (T rule); low case: the bird-scene rows
(0011/0012/0013 bird length) follow the agent instead (then -item(1.19, agent)).
P rows: lognormal label scatter 8% around the physical value (high) or around the agent's in-clip value (low);
expected = P(physical) weighted, P(physical) from calib_physb.py fits: 0053 .9, 0054 .75, 0047/0069 .8 / .95.
    .venv/bin/python research/next/accounting/expected.py"""
import re
import numpy as np, pandas as pd
from load import master, read, ROOT
from qp.mra import item_scores
from scored_set import fam
from qp.data import load_split
t = master()
v = load_split("val_hires"); vf = set(v.video_id.map(fam))
new_scored = t.scored & ~t.video_id.map(fam).isin(vf) & ~(t.video_id + "|" + t.question).duplicated(keep=False)
N_new = new_scored.groupby(t.category).sum()
c = pd.read_csv(ROOT / "research/next/accounting/changes_cand.csv")
c["new_scored"] = c.qid.map(new_scored)
print("changed rows:", len(c), "| old-set scored:", int(c.scored.sum()), "| new-set scored:", int(c.new_scored.sum()))
print(pd.crosstab([c.cat, c.src], [c.rule.str[0], c.new_scored]))
rng = np.random.default_rng(0)
def e(pred, truth, sig=0.08, n=4000):
    g = truth[None, :] * np.exp(rng.normal(0, sig, (n, len(truth))))
    return np.array([item_scores(pred, gi) for gi in g]).mean(axis=0)
c = c[c.new_scored].copy()
F = c[c.rule.eq("F")]; P = c[c.rule.str.startswith("P")]
bird = F.qid.isin([6, 1062, 1065])
gF_hi = 1 - item_scores(F.old.to_numpy(), F.new.to_numpy())
gF_lo = np.where(bird, -item_scores(F.new.to_numpy(), F.old.to_numpy()), gF_hi)
pp = {"internet_0053": .9, "internet_0054": .75, "internet_0047": .8, "internet_0069": .95}
gP_phys = e(P.new.to_numpy(), P.new.to_numpy()) - e(P.old.to_numpy(), P.new.to_numpy())
gP_incl = e(P.new.to_numpy(), P.old.to_numpy()) - e(P.old.to_numpy(), P.old.to_numpy())
w = P.video.map(pp).to_numpy()
res = []
for cat in ["D2", "D3"]:
    mf = F.cat.eq(cat).to_numpy(); mp = P.cat.eq(cat).to_numpy()
    hi = gF_hi[mf].sum() + gP_phys[mp].sum(); lo = gF_lo[mf].sum() + gP_incl[mp].sum()
    ex = gF_hi[mf].sum() * 0.85 + gF_lo[mf].sum() * 0.15 + (w * gP_phys + (1 - w) * gP_incl)[mp].sum()
    res.append(dict(cat=cat, N_new=int(N_new[cat]), F_rows=int(mf.sum()), P_rows=int(mp.sum()), items_expected=ex,
                    items_low=lo, items_high=hi, d_expected=ex / N_new[cat], d_low=lo / N_new[cat], d_high=hi / N_new[cat]))
r = pd.DataFrame(res); print(r.round(4).to_string(index=False))
print("overall expected %+.4f (low %+.4f, high %+.4f)" % (r.d_expected.sum() / 4, r.d_low.sum() / 4, r.d_high.sum() / 4))
for clip, g in P.groupby("video"):
    m = P.video.eq(clip).to_numpy()
    print(f"  {clip}: {m.sum()} rows, items if physical {gP_phys[m].sum():+.2f}, if in-clip {gP_incl[m].sum():+.2f}")
