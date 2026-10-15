"""Track A lever A1 (research/r86/PLAN.md): cross-family blend with GPT-6.1 Sol.

pred = exp(.75 ln base + .25 ln Sol) on scored, non-fact rows of S2 (all sources), D2 (simulation, segmented, internet)
and S3 (simulation and segmented). D3, lab rows and rows without a Sol answer keep the base answer. Segmented twins take
the original clip's Sol answer when the normalised question matches.

Gate (pre-registered in PLAN.md, run before any upload): (1) Sol answers >= 95% of the covered rows; (2) on the test
stated-fact rows of these subsets, scored on the raw routed answer before the facts rule (3D sim: the 3-run direct
median), the blend's mean item change >= 0 and no category has a net negative item sum.

    .venv/bin/python research/newmodels/build_sol_blend.py [BASE_CSV] [OUT_CSV]
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp import postprocess as pp  # noqa: E402
from qp.mra import item_scores  # noqa: E402

W = 0.25
BASE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "submissions/trackA_combo3_on_combo2.csv"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "submissions/trackA_cand_solblend_on_combo3.csv"


def read(p):
    d = pd.read_csv(p)
    return d.rename(columns={d.columns[0]: "id"}).set_index("id")["parsed_value"].astype(float)


t = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
base = read(BASE).reindex(t.index)
sol_raw = pd.to_numeric(pd.read_csv(ROOT / "runs/test_sol_high/test.csv").set_index("id").parsed_value,
                        errors="coerce")
sol_raw = sol_raw.where(sol_raw > 0)
# segmented twins -> original clip's answer to the same normalised question
orig = {(vid, pp.norm_question(q)): i for i, vid, q in zip(t.index, t.video_id, t.question)
        if not vid.endswith("_segmented")}
sol = sol_raw.reindex(t.index)
for i, vid, q in zip(t.index, t.video_id, t.question):
    if vid.endswith("_segmented") and np.isnan(sol.get(i, np.nan)):
        j = orig.get((vid[: -len("_segmented")], pp.norm_question(q)))
        if j is not None:
            sol[i] = sol_raw.get(j, np.nan)

is_fact = t.fact.notna() & np.isclose(base, t.fact.fillna(-1), rtol=1e-6)
cover = (t.category.eq("S2") | (t.category.eq("D2") & t.srcg.ne("lab")) | (t.category.eq("S3") & t.srcg.eq("sim")))
elig = cover & t.scored & ~is_fact
has = elig & sol.notna()
blend = base.copy()
blend[has] = np.exp((1 - W) * np.log(base[has]) + W * np.log(sol[has]))

print(f"eligible scored non-fact rows: {int(elig.sum())}; with a Sol answer: {int(has.sum())} "
      f"({has.sum() / max(elig.sum(), 1):.1%})  -> gate 1 {'PASS' if has.sum() >= .95 * elig.sum() else 'FAIL'}")
print("rows changed per category:", t.loc[has].category.value_counts().to_dict())
print("by subset:", t.loc[has].subset.value_counts().to_dict())
lr = np.log(sol[has] / base[has])
print(f"median |log(Sol/base)| on changed rows {lr.abs().median():.3f}; share > log 1.5: {(lr.abs() > np.log(1.5)).mean():.1%}")

# gate 2: stated facts of the covered subsets, raw routed answer (3D sim: dmed) before the facts rule
raw = t.r_parsed_value.where(~(t.category.isin(["S3", "D3"]) & t.srcg.eq("sim")), t.dmed)
fm = cover & t.fact.notna() & raw.notna() & sol.notna()
rb = np.exp((1 - W) * np.log(raw[fm]) + W * np.log(sol[fm]))
d = pd.Series(item_scores(rb.to_numpy(), t.fact[fm].to_numpy()) - item_scores(raw[fm].to_numpy(), t.fact[fm].to_numpy()),
              index=t.index[fm])
per = d.groupby(t.category[fm]).agg(["size", "sum", "mean"])
print("gate 2 (stated facts, raw routed answer):"); print(per.round(3).to_string())
g2 = d.mean() >= 0 and (per["sum"] >= 0).all()
print(f"gate 2 mean change {d.mean():+.4f} on {int(fm.sum())} rows -> {'PASS' if g2 else 'FAIL'}")

with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
    pd.DataFrame({"id": blend.index, "parsed_value": blend.values}).to_csv(fh, index=False)
subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(OUT)], check=True)
