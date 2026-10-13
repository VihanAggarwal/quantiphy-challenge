"""Foreshortening bias: horizontal extents (length / width) of 3D-sim objects read low through a camera looking at them
obliquely.  Test a fixed upward factor exp(beta) on length/width size rows (heights untouched):
 (1) validation rows (evaluation only), applied on top of the CURRENT submission values (what a candidate would do),
     only non-fact rows;  (2) exact stated facts (label-free), applied to the raw 3-run median and to raw x K(LOFO).
Clip-clustered bootstrap CIs."""
from common import *  # noqa
import pickle
ctxd = pickle.loads(Path(__file__).with_name("out_ctx.pkl").read_bytes())
spec = ctxd["spec"]
test = test_df().set_index("qid")
tab = pd.read_csv(ROOT / "research/simfov/out/table.csv").set_index("qid")
cur = read_sub()
lv = val_labels(); lf, flog = fact_labels(tab.dmed)
flog = flog.set_index(flog.qid.astype(int))
HOR = {"length", "width"}
BETAS = (0.03, 0.05, 0.08, 0.12)


def report(name, base, lab, clips, hor):
    S0 = item_scores(base, lab)
    out = [f"{name}: n={len(lab)} (horizontal {int(hor.sum())}) clips={clips.nunique()} base {np.mean(S0):.3f}"]
    for b in BETAS:
        p = np.where(hor, base * np.exp(b), base)
        S = item_scores(p, lab)
        d, lo, hi = boot_delta(pd.Series(S, index=lab.index), pd.Series(S0, index=lab.index), clips)
        out.append(f"   beta {b:.2f}: {np.mean(S):.3f}  delta/row {d:+.4f} [{lo:+.4f}, {hi:+.4f}]  "
                   f"per horizontal row {d * len(lab) / max(hor.sum(), 1):+.4f}")
    print("\n".join(out))


# (1) validation, non-fact rows of 3D sim, current values
v = tab[tab.index.isin(lv.index) & ~tab.index.isin(lf.index) & (tab.kind == "size")]
hor = np.array([spec[q].dim in HOR for q in v.index])
report("VAL 3D-sim sizes (current submission)", cur.reindex(v.index).to_numpy(), lv.reindex(v.index),
       clip_cluster(v.video_id), hor)
report("VAL 3D-sim sizes (raw median)", v.dmed.to_numpy(), lv.reindex(v.index), clip_cluster(v.video_id), hor)
# (2) facts: raw and raw x K-LOFO
f = tab[tab.index.isin(lf.index) & (tab.kind == "size")]
hor = np.array([spec[q].dim in HOR for q in f.index])
report("FACTS 3D-sim sizes (raw median)", f.dmed.to_numpy(), lf.reindex(f.index), clip_cluster(f.video_id), hor)
kl = []
for q in f.index:
    vv = test.video_id[q]
    line = flog.loc[q, "reason"]
    ls = [np.log(lf[p] / tab.dmed[p]) for p in lf.index if p != q and p in tab.index and test.video_id[p] == vv
          and tab.kind[p] in ("size", "speed") and flog.loc[p, "reason"] != line]
    kl.append(np.median([0.0] + ls))
report("FACTS 3D-sim sizes (raw x K-LOFO)", f.dmed.to_numpy() * np.exp(kl), lf.reindex(f.index), clip_cluster(f.video_id), hor)
for cat in ("S3", "D3"):
    m = (f.category == cat).to_numpy()
    report(f"FACTS {cat} (raw)", f.dmed.to_numpy()[m], lf.reindex(f.index[m]), clip_cluster(f.video_id[m]), hor[m])
# test rows that would change
t = tab[(tab.kind == "size") & ~tab.index.isin(lf.index) & ~tab.index.isin(lv.index)]
h = np.array([spec[q].dim in HOR for q in t.index])
print("\nscored test rows that a horizontal-extent factor would change:", int(h.sum()),
      pd.Series(t.category.to_numpy()[h]).value_counts().to_dict())
