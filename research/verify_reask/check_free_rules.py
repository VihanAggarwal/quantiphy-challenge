"""Re-check the report's unscripted claim: free combination rules on the existing 3D non-lab runs
(most-confident run, confidence-weighted log mean) vs the 3-run median, on validation (EVALUATION ONLY)
and on test stated-fact rows (exact labels stated in other clips' priors). Builds no answers."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "research/reask"))
from features import run_table  # noqa: E402
from qp.mra import item_scores  # noqa: E402


def rules(runs, lab):
    V = pd.concat([x.direct_value for x in runs], axis=1)
    C = pd.concat([x.conf for x in runs], axis=1).reindex(V.index)
    L = np.log(V.where(V > 0))
    med = np.exp(L.median(axis=1))
    Cm = C.where(L.notna()).fillna(-1)
    best = np.exp(pd.Series([L.iloc[i, int(np.argmax(Cm.iloc[i].to_numpy()))] for i in range(len(L))], index=L.index))
    w = C.where(L.notna()).fillna(0).clip(lower=0.05)
    wmean = pd.Series(np.exp((L.fillna(0).to_numpy() * w.to_numpy()).sum(1) / w.to_numpy().sum(1)), index=L.index)
    out = {"single0": V.iloc[:, 0], "single1": V.iloc[:, 1], "single2": V.iloc[:, 2], "median3": med,
           "most_conf": best, "conf_wmean": wmean}
    return {k: np.nanmean(item_scores(v, lab)) for k, v in out.items()}


from qp.data import load_validation  # noqa: E402
r = pd.read_csv(ROOT / "research/reask/val_rows.csv").set_index("qid")
idx = r.index[r.src == "3Dnl"]
vb = run_table("runs/val_hr_v1_high", "val_hires").reindex(idx)
v1 = run_table("runs/val_opus_high", "val").reindex(idx)
v2 = run_table("runs/val_hr_v2_high", "val_hires").reindex(idx)
print("validation 3Dnl n=%d" % len(idx), {k: round(v, 3) for k, v in rules([vb, v1, v2], r.answer.reindex(idx)).items()})

t = pd.read_csv(ROOT / "research/reask/test_rows.csv").set_index("qid")
fi = t.index[t.fact.notna() & (t.src == "3Dnl")]
runs = [run_table(p, "test").reindex(fi) for p in ["runs/test_v1_high_854", "runs/test_3dnl_v1_high_b",
                                                   "runs/test_3dnl_v2_high"]]
print("test facts 3Dnl n=%d" % len(fi), {k: round(v, 3) for k, v in rules(runs, t.fact.reindex(fi)).items()})
print("fact rows by video:", t.loc[fi].video_id.nunique(), "videos; top:", t.loc[fi].video_id.value_counts().head(5).to_dict())
