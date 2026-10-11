"""Probe 7 part: median of three Claude runs' direct answers on the 3D non-lab questions, on top of probe 5.

Runs: test_v1_high_854 (base), test_3dnl_v1_high_b (second v1 sample), test_3dnl_v2_high (v2 prompt, 854 px).
Validation: a 3-run median of direct answers beat the single run by +0.020 per 3D non-lab question (14 of 15
run combinations >= 0). Probe 5's answers are rescaled by ensemble/base (so its per-clip scale correction and
pooling carry over), except rows already set to a value stated by the scene family (kept exact); segmented
twins are then re-synced from their originals (qp.postprocess twin rule). Only S3/D3 rows change.

    python research/ensemble_3dnl.py OUT.csv
"""
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, ".")
from qp import postprocess as pp  # noqa: E402
from qp.data import load_test  # noqa: E402

t = load_test().set_index("qid")
m = (t.video_type.str[1] == "3") & (t.video_source != "lab") & t.category.isin(["S3", "D3"])
r = lambda p: pd.read_csv(p).set_index("id")["direct_value"].reindex(t.index)  # noqa: E731
base = r("runs/test_v1_high_854/test.csv")
runs = [base, r("runs/test_3dnl_v1_high_b/test.csv"), r("runs/test_3dnl_v2_high/test.csv")]
ratio = (np.exp(np.log(pd.concat(runs, axis=1)).median(axis=1)) / base).where(m, 1.0)
p5 = pd.read_csv("submissions/trackA_probe5_families_merged.csv",
                 float_precision="round_trip").set_index("id").parsed_value.reindex(t.index)
_, log = pp.apply_rules(p5, t.reset_index(), rules=("facts",))
facts = log[log.rule == "facts"]
fact_rows = {int(q) for q, v in zip(facts.qid, facts.new) if np.isclose(p5[int(q)], v, rtol=1e-6)}
new = p5.copy()
adj = m & ~t.index.isin(list(fact_rows))
new[adj] = p5[adj] * ratio[adj]
new = pp.apply_rules(new, t.reset_index(), rules=("twin",))[0].reindex(t.index)
out = p5.copy()
sel = t.category.isin(["S3", "D3"])
out[sel] = new[sel]
pd.DataFrame({"id": out.index, "parsed_value": out.values}).to_csv(sys.argv[1], index=False)
print(f"{int((~np.isclose(out, p5, rtol=1e-9)).sum())} S3/D3 answers changed vs probe 5")
