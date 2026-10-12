"""Same object + same question across a scene family, answered under a SIZE prior (S2: scale from a stated
size, an exact label) and under a MOTION prior (D2). log(D2 / S2) per pair; aggregated per D2 clip and per
prior kind. Uses raw pipeline answers (pre-family pooling) so the two sides are independent measurements.
Test inputs only."""
import itertools, sys
import numpy as np
import pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from common import *
from qp import postprocess as pp

d = pd.read_pickle(ROOT / "research/d2static/out/test_table.pkl")
df = load_split("test")
facts = pp._parse_facts(pp._questions(df))
links = pp.scene_links(pp._questions(df), facts, pp.FrameCache(pp.DEFAULT_CACHE))
fam = pp.scene_families(df, links, pp.SIZE_LINKS)
d["fam"] = d.video_id.map(fam)
d["nq"] = d.question.map(pp.norm_question)
x = d[d.category.isin(["S2", "D2", "S3", "D3"]) & d.tkind.isin(["size", "distance"])]
rows = []
for (f, nq), g in x.groupby(["fam", "nq"]):
    a = g[g.category == "D2"]
    b = g[g.category.isin(["S2"])]
    for qa, ra in a.iterrows():
        for qb, rb in b.iterrows():
            if pp.base_id(ra.video_id) == pp.base_id(rb.video_id):
                continue
            rows.append(dict(fam=f, nq=nq, qa=qa, va=ra.video_id, pa=ra.prior, pk=ra.pkind, qb=qb, vb=rb.video_id,
                             pb=rb.prior, A=ra.raw, B=rb.raw, A8=ra.p8, B8=rb.p8, tk=ra.tkind, src=ra.video_source))
r = pd.DataFrame(rows)
r["lr"] = np.log(r.A / r.B)
r.to_csv(ROOT / "research/d2static/out/cross_prior.csv", index=False)
print(len(r), r.qa.nunique(), r.va.nunique())
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 400); pd.set_option("display.max_colwidth", 50)
print(r.groupby("pk").lr.describe())
print(r.groupby(["va", "pa"]).agg(n=("lr", "size"), med=("lr", "median"), vbs=("vb", lambda s: ",".join(sorted(set(s))))).round(3).to_string())
