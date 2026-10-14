"""Held-out label sets for the gate study (EVALUATION ONLY; labels never written to test answers).
  val:   validation labels of identical test questions (test qid -> label)
  facts: exactly-known stated-fact rows on test (qp.postprocess 'facts' rule), value = stated fact
Writes research/gates/out/evalsets.csv (qid, set, label)."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from qp import postprocess as pp
from qp.data import load_split, load_validation
test = load_split("test"); val = load_validation()
key = lambda d: list(zip(d.video_id, d.question.map(pp.norm_question)))
vmap = dict(zip(key(val), val.answer))
lab_v = pd.Series([vmap.get(k, np.nan) for k in key(test)], index=test.qid).dropna()
base = pd.read_csv(ROOT / "research/gates/out/base.csv").set_index("qid")
_, log = pp.apply_rules(base.dir_a.reindex(test.qid).fillna(1.0), test, rules=("facts",), speed_guard=0)
f = log[log.applied]
lab_f = pd.Series(f.new.to_numpy(float), index=f.qid.astype(int))
out = pd.concat([pd.DataFrame({"qid": lab_v.index, "set": "val", "label": lab_v.values}),
                 pd.DataFrame({"qid": lab_f.index, "set": "facts", "label": lab_f.values})])
out.to_csv(ROOT / "research/gates/out/evalsets.csv", index=False)
b = base.reindex(out.qid); out["cat"] = b.category.values; out["sub"] = b["sub"].values; out["kind"] = b.kind.values
print(out.groupby(["set", "cat", "sub", "kind"]).size().to_string())
print("val&facts overlap:", len(set(lab_v.index) & set(lab_f.index)))
