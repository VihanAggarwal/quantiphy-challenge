"""Held-out stated-fact test of pooling equivalent static-size questions across 2D-simulation family clips (S2/D2):
for every size question that a sibling's prior answers exactly (facts rule log, old = the raw pipeline answer), compare
the clip's own raw answer with the geometric mean of the raw answers to the same normalized question in the other
clips of the family (pp scene families). Test inputs only."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from qp import postprocess as pp
from qp.data import load_test
from qp.mra import item_scores
t = load_test()
run = pd.read_csv(ROOT / "runs/test_v1_high_854/test.csv").set_index("id")
t["raw"] = t.qid.map(run.parsed_value)
df = pp._questions(t); facts = pp._parse_facts(df); links = pp.scene_links(df, facts, None)
fam = pp.scene_families(df, links, pp.SIZE_LINKS)
t["fam"] = t.video_id.map(fam); t["nq"] = t.question.map(pp.norm_question)
log = pd.read_csv(ROOT / "research/path85_s2sim/out_facts_log.csv")
log = log[log.applied & log.category.isin(["S2", "D2"]) & (log.kind == "size") & log.video_id.str.startswith("simulation")]
rows = []
tt = t.set_index("qid")
for r in log.itertuples():
    a = tt.loc[r.qid]
    sib = tt[(tt.fam == a.fam) & (tt.nq == a.nq) & (tt.index != r.qid) & tt.raw.notna() & (tt.category.isin(["S2", "D2"]))]
    sib = sib[~sib.video_id.str.replace("_segmented", "").eq(a.video_id.replace("_segmented", ""))]
    if len(sib) == 0: continue
    pooled = float(np.exp(np.log(np.r_[sib.raw.to_numpy(float), a.raw]).mean()))
    rows.append(dict(qid=r.qid, video_id=a.video_id, cat=a.category, q=a.question[:50], fact=r.new, own=a.raw, pooled=pooled, nsib=len(sib)))
d = pd.DataFrame(rows)
d["s_own"] = item_scores(d.own, d.fact); d["s_pool"] = item_scores(d.pooled, d.fact)
pd.set_option("display.width", 220)
print(d.round(3).to_string())
print("n", len(d), "own", d.s_own.mean().round(3), "pooled", d.s_pool.mean().round(3), "| median |ln| own", np.median(np.abs(np.log(d.own / d.fact))).round(3), "pooled", np.median(np.abs(np.log(d.pooled / d.fact))).round(3))
