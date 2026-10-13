"""Consensus K: a clip's scale error estimated from its answers on objects OTHER clips of the scene family also
answer (no stated facts used), K_cons = median_o log(median of the other clips' answers on o / own answer on o).
Label-free test: on clips that also have stated-fact rows, does K_cons predict the facts' misses
(K_fact = log(stated / own answer))?  Answers = Claude direct, log-median of 3 runs (pre-rule), 3D sim rows."""
from common import *  # noqa
import pickle
from collections import defaultdict

ctxd = pickle.loads(Path(__file__).with_name("out_ctx.pkl").read_bytes())
test = test_df()
df = pp._questions(test)
tab = pd.read_csv(ROOT / "research/simfov/out/table.csv").set_index("qid")
raw = tab.dmed
lf, flog = fact_labels()

class C:  # minimal ctx for equivalent_questions
    pass
ctx = C()
ctx.df = df; ctx.spec = ctxd["spec"]; ctx.fam_size = ctxd["fam_size"]; ctx.fam_motion = ctxd["fam_motion"]
ctx.scen = ctxd["scen"]; ctx.depth = ctxd["depth"]; ctx.row = {int(r.qid): r for r in df.itertuples()}
eq = pp.equivalent_questions(ctx, list(raw.index))

KINDS = sys.argv[1].split(",") if len(sys.argv) > 1 else ["size"]
rows = []
for v, g in df[df.qid.isin(raw.index)].groupby("video_id"):
    kf, kc, objs = [], [], []
    for q in g.qid:
        s = ctx.spec[q]
        if q in lf.index:
            if s.kind in ("size", "speed"):
                kf.append(np.log(lf[q] / raw[q]))
            continue
        if s.kind not in KINDS or q not in eq:
            continue
        others = [p for p in eq[p0] if False] if False else [p for p in eq[q] if p in raw.index and p not in lf.index
                                                            and pp.base_id(ctx.row[p].video_id) != pp.base_id(v)]
        if not others:
            continue
        # one vote per other base clip
        votes = defaultdict(list)
        for p in others:
            votes[pp.base_id(ctx.row[p].video_id)].append(np.log(raw[p] * ctx.spec[p].to_si))
        o = np.median([np.mean(x) for x in votes.values()])
        kc.append(o - np.log(raw[q] * s.to_si))
    rows.append(dict(video=v, cat=g.category.iloc[0], n_fact=len(kf), K_fact=np.median(kf) if kf else np.nan,
                     n_cons=len(kc), K_cons=np.median(kc) if kc else np.nan))
R = pd.DataFrame(rows)
R.to_csv(Path(__file__).with_name("out_kcons.csv"), index=False)
both = R[(R.n_fact > 0) & (R.n_cons > 0)]
print(f"kinds {KINDS}: clips {len(R)}, with facts {int((R.n_fact>0).sum())}, with consensus {int((R.n_cons>0).sum())}, both {len(both)}")
print("clips with consensus but NO facts:", int(((R.n_fact == 0) & (R.n_cons > 0)).sum()), R[(R.n_fact == 0) & (R.n_cons > 0)].groupby('cat').size().to_dict())
pd.set_option("display.width", 200)
print(both.round(3).to_string())
if len(both) > 2:
    print("corr K_fact vs K_cons:", round(np.corrcoef(both.K_fact, both.K_cons)[0, 1], 3),
          " sign agreement (|K_fact|>.05):", ((np.sign(both.K_fact) == np.sign(both.K_cons)) | (both.K_fact.abs() < .05)).mean().round(3))
