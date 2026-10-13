"""Exact stated facts (label-free test checks): run the stated-value rules on the raw run answers and log them."""
from common import *
from qp.postprocess import apply_rules
t = pd.read_pickle(OUT / "table.pkl")
pred = t.r_parsed_value.astype(float).fillna(1.0)
new, log = apply_rules(pred, t.reset_index(), rules=("facts", "motionfam", "freefall", "labfacts"))
log = log[log.applied & log.new.notna()]
log.to_csv(OUT / "facts_log.csv", index=False)
print(len(log)); print(log.rule.value_counts())
