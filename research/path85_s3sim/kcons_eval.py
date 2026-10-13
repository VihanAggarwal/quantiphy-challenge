"""Evaluate consensus K (kcons.py) as a predictor on (1) exact stated-fact rows (label-free) and (2) validation rows
(evaluation only) that are NOT in any pooled group (the rows a K_cons rule would actually change).
pred = raw * exp(lam * K_cons), K_cons from size answers on objects shared with other base clips of the family."""
from common import *  # noqa
import pickle
from collections import defaultdict

ctxd = pickle.loads(Path(__file__).with_name("out_ctx.pkl").read_bytes())
test = test_df()
df = pp._questions(test)
tab = pd.read_csv(ROOT / "research/simfov/out/table.csv").set_index("qid")
raw = tab.dmed
lf, flog = fact_labels()
lv = val_labels()

class C:
    pass
ctx = C()
ctx.df = df; ctx.spec = ctxd["spec"]; ctx.fam_size = ctxd["fam_size"]; ctx.fam_motion = ctxd["fam_motion"]
ctx.scen = ctxd["scen"]; ctx.depth = ctxd["depth"]; ctx.row = {int(r.qid): r for r in df.itertuples()}
eq = pp.equivalent_questions(ctx, list(raw.index))


def kcons(v, exclude, kinds=("size",)):
    """per-object log offsets of clip v vs the other base clips (objects in `exclude` qids skipped)."""
    out = []
    for q in df.qid[df.video_id == v]:
        s = ctx.spec[q]
        if q in exclude or q not in raw.index or s.kind not in kinds or q not in eq:
            continue
        others = [p for p in eq[q] if p in raw.index and p not in exclude and
                  pp.base_id(ctx.row[p].video_id) != pp.base_id(v)]
        if not others:
            continue
        votes = defaultdict(list)
        for p in others:
            votes[pp.base_id(ctx.row[p].video_id)].append(np.log(raw[p] * ctx.spec[p].to_si))
        out.append(np.median([np.mean(x) for x in votes.values()]) - np.log(raw[q] * s.to_si))
    return out


fact_q = set(lf.index)
res = []
for name, lab in (("FACTS", lf), ("VAL", lv)):
    for q in lab.index:
        if q not in raw.index:
            continue
        v = ctx.row[q].video_id
        s = ctx.spec[q]
        if s.kind not in ("size", "speed"):
            continue
        if name == "VAL" and (q in eq or q in fact_q):   # val rows a K rule would change: unpooled, not facts
            continue
        ks = kcons(v, fact_q | {q})
        if not ks:
            continue
        res.append(dict(src=name, qid=q, video=v, cat=ctx.row[q].category, kind=s.kind, n=len(ks),
                        K=float(np.median(ks)), raw=raw[q], lab=lab[q]))
R = pd.DataFrame(res)
for lam in (0.5, 1.0):
    R[f"k{lam}"] = R.raw * np.exp(lam * R.K)
R["kshr"] = R.raw * np.exp(R.K * R.n / (R.n + 1))
R["kgate"] = np.where((R.n >= 2) & (R.K.abs() > 0.1), R.raw * np.exp(R.K), R.raw)
cols = ["raw", "k0.5", "k1.0", "kshr", "kgate"]
for (src, cat), g in R.groupby(["src", "cat"]):
    S = pd.DataFrame({c: item_scores(g[c], g.lab) for c in cols}, index=g.index)
    print(f"== {src} {cat}: n={len(g)} clips={clip_cluster(g.video).nunique()}  " +
          "  ".join(f"{c} {S[c].mean():.3f}" for c in cols))
    for c in cols[1:]:
        print(f"     {c} - raw {[round(x, 3) for x in boot_delta(S[c], S.raw, clip_cluster(g.video))]}")
    for kind, gk in g.groupby("kind"):
        Sk = S.loc[gk.index]
        print(f"     kind {kind} n={len(gk)}: " + "  ".join(f"{c} {Sk[c].mean():.3f}" for c in cols))
R.to_csv(Path(__file__).with_name("out_kcons_eval.csv"), index=False)
