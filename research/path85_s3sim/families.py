"""Scene families of the 3D simulation clips (qp.postprocess links) and which links join them. Cached to out_ctx.pkl."""
from common import *  # noqa
import pickle
from collections import defaultdict
test = test_df()
df = pp._questions(test)
frames = pp.FrameCache()
ctx = pp._Ctx(df, frames)
pk = Path(__file__).with_name("out_ctx.pkl")
pk.write_bytes(pickle.dumps(dict(fam_size=ctx.fam_size, fam_motion=ctx.fam_motion, scen=ctx.scen, links=ctx.links,
                                 spec=ctx.spec, depth=ctx.depth, accel=dict(ctx.accel))))
sim = df[df.video_id.str.startswith("simulation") & df.category.isin(["S3", "D3"])]
fams = defaultdict(set)
for v in sim.video_id.unique():
    fams[ctx.fam_size[v]].add(v)
for f, vs in sorted(fams.items(), key=lambda x: -len(x[1])):
    if len(vs) < 2:
        continue
    bases = sorted({pp.base_id(v) for v in vs})
    print(f"FAM {f}: {len(bases)} base clips: {' '.join(b.replace('simulation_','') for b in bases)}")
    for b in bases:
        r = sim[sim.video_id == b]
        if len(r):
            print(f"    {b.replace('simulation_','')} {r.category.iloc[0]} motion-fam {ctx.fam_motion[b].replace('simulation_','')} scen {ctx.scen[b].replace('simulation_','')} | {r.prior.iloc[0][:60]}")
