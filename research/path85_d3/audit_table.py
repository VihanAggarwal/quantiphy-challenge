"""Coverage audit table: every S3/D3 non-lab row with raw run values, ensemble median, current value, families."""
from common import *
import pickle

t = test_df().copy()
cur = read_sub()
D = runs_direct()
G = runs_geo()
t = t.set_index("qid")
t["cur"] = cur.reindex(t.index)
for r in RUNS:
    t["d_" + r] = D[r].reindex(t.index)
t["ens"] = lmed(D.reindex(t.index))
t["geo1"] = G[RUNS[0]].reindex(t.index)
run1 = pd.read_csv(ROOT / "runs" / RUNS[0] / "test.csv").set_index("id")
t["method1"] = run1["method"].reindex(t.index)
vl = val_labels()
t["val"] = vl.reindex(t.index)
# family structure from qp.postprocess (test inputs only)
df = pp._questions(load_split("test"))
frames = pp.FrameCache()
ctx = pp._Ctx(df, frames)
t["fam_size"] = [ctx.fam_size[v] for v in t.video_id]
t["fam_motion"] = [ctx.fam_motion[v] for v in t.video_id]
t["kind"] = [ctx.spec[q].kind for q in t.index]
t["objs"] = ["|".join(ctx.spec[q].objs) for q in t.index]
t["time"] = [ctx.spec[q].time for q in t.index]
t["base"] = t.video_id.map(pp.base_id)
# stated facts (exact) per qid, speed guard off
_, flog = pp.apply_rules(pd.Series(1.0, index=t.index), load_split("test"), rules=("facts",), speed_guard=0)
fa = flog[flog.applied]
t["fact"] = pd.Series(fa.new.to_numpy(float), index=fa.qid.astype(int)).reindex(t.index)
t["fact_src"] = pd.Series(fa.source_clip.to_numpy(), index=fa.qid.astype(int)).reindex(t.index)
frames.save()
nl = t[(t.category.isin(["S3", "D3"])) & (t.video_source != "lab")].copy()
def status(r):
    if np.isfinite(r.fact) and np.isclose(r.cur, r.fact, rtol=1e-6):
        return "fact"
    if np.isfinite(r.ens) and np.isclose(r.cur, r.ens, rtol=1e-6):
        return "ens_raw"
    if any(np.isfinite(r["d_" + x]) and np.isclose(r.cur, r["d_" + x], rtol=1e-6) for x in RUNS):
        return "one_run"
    if np.isfinite(r.geo1) and np.isclose(r.cur, r.geo1, rtol=1e-6):
        return "geo"
    return "modified"
nl["status"] = nl.apply(status, axis=1)
nl["fam_n_base"] = nl.fam_size.map(t.groupby("fam_size").base.nunique())
nl.to_pickle(OUT / "audit_nl.pkl")
pickle.dump(dict(links=ctx.links), open(OUT / "links.pkl", "wb"))
for c in ["D3", "S3"]:
    x = nl[nl.category == c]
    print(c, len(x), "scored~", int(x.val.isna().sum()))
    print(pd.crosstab(x.status, x.kind, margins=True))
    print(pd.crosstab(x.status, x.fam_n_base.clip(upper=5), margins=True))
