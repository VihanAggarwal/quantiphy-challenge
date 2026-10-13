"""Cross-camera radial bound: a constant-speed object's speed >= |dr/dt| measured in EVERY camera that lists its
timed depth (same event).  Label-free check of current speed answers on 3D sim rows: how often is the answer
below the max radial speed over the same-event cameras (and over its own clip only)?"""
from common import *  # noqa
import pickle
ctxd = pickle.loads(Path(__file__).with_name("out_ctx.pkl").read_bytes())
test = test_df().set_index("qid")
cur = read_sub()
tab = pd.read_csv(ROOT / "research/simfov/out/table.csv").set_index("qid")
lf, _ = fact_labels(); lv = val_labels()
spec, depth, scen, famm = ctxd["spec"], ctxd["depth"], ctxd["scen"], ctxd["fam_motion"]

def radial(v, obj):
    best = None
    for k, e in depth[v].items():
        te = [x for x in e if x[0] is not None]
        if len(te) >= 2 and (pp._mf_match(k, obj) or pp.name_score(k, obj) >= 0.6):
            (t0, r0), (t1, r1) = te[0], te[-1]
            if t1 > t0:
                best = (abs(r1 - r0) / (t1 - t0), (t0, t1), tuple(te))
    return best

out = []
for q in tab.index:
    s = spec[q]
    if s.kind != "speed" or len(s.objs) != 1:
        continue
    v = test.video_id[q]
    obj = s.objs[0]
    own = radial(v, obj)
    same = [c for c in set(test.video_id) if c != v and (scen.get(c) == scen.get(v) or pp.base_id(c) == pp.base_id(v))]
    others = [(c, radial(c, obj)) for c in same]
    others = [(c, r) for c, r in others if r is not None and (own is None or r[1] == own[1])]
    vmax = max([r[0] for _, r in others] + ([own[0]] if own else []), default=np.nan)
    out.append(dict(qid=q, video=v, cat=test.category[q], obj=obj, cur=cur[q] * s.to_si, dmed=tab.dmed[q] * s.to_si,
                    own_rad=own[0] if own else np.nan, max_rad=vmax, n_cam=len(others) + (1 if own else 0),
                    fact=lf.get(q, np.nan), val=lv.get(q, np.nan), q=test.question[q][:70]))
R = pd.DataFrame(out)
R["below_own"] = R.cur < R.own_rad
R["below_max"] = R.cur < R.max_rad
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 70)
print("speed rows", len(R), "with own radial", R.own_rad.notna().sum(), "multi-camera (n_cam>=2)", (R.n_cam >= 2).sum())
print("cur below own radial:", R.below_own.sum(), " cur below cross-camera max radial:", R.below_max.sum())
print(R[R.below_max | (R.cur < 1.05 * R.max_rad)].round(3).to_string())
R.to_csv(Path(__file__).with_name("out_radial_bound.csv"), index=False)
