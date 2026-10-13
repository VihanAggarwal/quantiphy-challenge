"""Run the 'facts' rule on the raw run answers to list exact stated facts usable as label-free checks."""
from common import *
from qp.postprocess import apply_rules
t = test_table()
pred = t.run_parsed_value.astype(float)
new, log = apply_rules(pred, t.reset_index(), rules=("facts",))
log = log.merge(t[["video_id", "category", "video_source", "question", "prior", "kind", "run_geo_value", "run_direct_value", "base"]],
                left_on="qid", right_index=True)
log.to_csv(Path(__file__).parent / "out_facts_log.csv", index=False)
a = log[log.applied]
print(len(log), len(a))
print(pd.crosstab([a.category, a.video_source], a.kind))
