"""Stated-fact table on the test set: every question whose target a scene-family clip states as a prior,
with the raw pipeline answer (geometry/direct) and the probe-8 base answer. Test inputs only."""
import sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp.data import load_split
from qp import postprocess as pp

OUT = ROOT / "research/d2static/out"
OUT.mkdir(parents=True, exist_ok=True)

df = load_split("test")
frames = pp.FrameCache(pp.DEFAULT_CACHE)
cand = pp.stated_facts(df, frames)
raw = pd.read_csv(ROOT / "runs/test_v1_high_854/test.csv").set_index("id")
base = pd.read_csv(ROOT / "submissions/trackA_probe8_p7b_d2fixes_d3labphys.csv")
base = base.set_index("id")["parsed_value"]
q = df.set_index("qid")
cand["category"] = cand.qid.map(q.category)
cand["prior"] = cand.qid.map(q.prior)
cand["question"] = cand.qid.map(q.question)
cand["fps"] = cand.qid.map(q.fps)
cand["raw"] = cand.qid.map(raw.parsed_value)
cand["geo"] = cand.qid.map(raw.geo_value)
cand["direct"] = cand.qid.map(raw.direct_value)
cand["method"] = cand.qid.map(raw.method)
cand["p8"] = cand.qid.map(base)
cand.to_csv(OUT / "facts_test.csv", index=False)
print(len(cand), cand.category.value_counts().to_dict())
