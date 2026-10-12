"""Validation (EVALUATION ONLY): how often are flagged questions wrong, and what would a re-ask recover?

A re-ask is simulated with the cached validation runs: a second sample of the same pipeline
(val_opus_high = v1 high, 480p frames), the v2 prompt (val_hr_v2_high), more samples (med, med2, fable,
xhigh) and the verify pass (val_verify_high: Claude high re-reads its own tracks with zoomed crops and
may correct them). Base = val_hr_v1_high (v1 high, the test pipeline's configuration).

    .venv/bin/python research/reask/val_eval.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from features import add_prior_ratio, run_table  # noqa: E402
from qp.data import load_validation  # noqa: E402
from qp.mra import item_scores  # noqa: E402

v = load_validation().set_index("qid")
base = add_prior_ratio(run_table("runs/val_hr_v1_high", "val_hires"), v.target_unit)
base = base.join(v[["category", "video_source", "answer", "question"]])
base["src"] = np.where(base.category.str[1] == "2", "2D",
                       np.where(base.video_source == "lab", "lab", "3Dnl"))


def col(run, split, c="parsed_value"):
    return pd.read_csv(ROOT / run / f"{split}.csv").set_index("id")[c].reindex(base.index)


ALT = {"v1b": col("runs/val_opus_high", "val"), "v2": col("runs/val_hr_v2_high", "val_hires"),
       "med": col("runs/val_opus_med", "val"), "med2": col("runs/val_opus_med2", "val"),
       "fable": col("runs/val_fable_high", "val"), "v2b": col("runs/val_v2_high", "val")}
DIR = {"base": base.direct_value, "v1b": col("runs/val_opus_high", "val", "direct_value"),
       "v2": col("runs/val_hr_v2_high", "val_hires", "direct_value"),
       "med": col("runs/val_opus_med", "val", "direct_value"),
       "med2": col("runs/val_opus_med2", "val", "direct_value"),
       "fable": col("runs/val_fable_high", "val", "direct_value")}
VER = pd.read_csv(ROOT / "runs/val_verify_high/val.csv").set_index("id").reindex(base.index)

S = lambda p: item_scores(p, base.answer)  # noqa: E731
sc = pd.DataFrame({"base": S(base.parsed_value), **{k: S(a) for k, a in ALT.items()},
                   "verify_final": S(VER.final_answer), "verify_parsed": S(VER.parsed_value),
                   "verify_pass1": S(VER.pass1_value)}, index=base.index)


def gmed(cols):
    x = np.log(pd.concat(cols, axis=1).where(lambda d: d > 0))
    return np.exp(x.median(axis=1, skipna=True))


med3 = gmed([base.parsed_value, ALT["v1b"], ALT["v2"]])
med5 = gmed([base.parsed_value, ALT["v1b"], ALT["v2"], ALT["med"], ALT["med2"]])
sc["med3"] = S(med3.fillna(base.parsed_value))
sc["med5"] = S(med5.fillna(base.parsed_value))
sc["mean_1alt"] = sc[["v1b", "v2"]].mean(axis=1)          # expected score of ONE fresh re-ask (v1 or v2)
sc["oracle3"] = sc[["base", "v1b", "v2"]].max(axis=1)
# spread among the three test-equivalent samples (what test has on 3D non-lab)
L = np.log(pd.concat([base.parsed_value, ALT["v1b"], ALT["v2"]], axis=1).where(lambda d: d > 0))
base["spread3"] = L.max(axis=1) - L.min(axis=1)
Ld = np.log(pd.concat([DIR["base"], DIR["v1b"], DIR["v2"]], axis=1).where(lambda d: d > 0))
base["dspread3"] = Ld.max(axis=1) - Ld.min(axis=1)

flags = {
    "all": pd.Series(True, index=base.index),
    "gd>0.2": base.gd > 0.2,
    "gd>0.4": base.gd > 0.4,
    "conf<=0.3": base.conf <= 0.3,
    "conf<=0.2": base.conf <= 0.2,
    "spread3>0.15": base.spread3 > 0.15,
    "spread3>0.3": base.spread3 > 0.3,
    "dspread3>0.15": base.dspread3 > 0.15,
    "beyond_end": base.beyond,
    "cov_gap>0.25s": base.cov_gap > 0.25,
    "prior_ratio_out": (base.prior_ratio > 10) | (base.prior_ratio < 0.1),
    "direct_routed": base.method == "direct",
    "motion": base.motion,
}
out = []
for grp in ["ALL", "2D", "lab", "3Dnl"]:
    g = base.index if grp == "ALL" else base.index[base.src == grp]
    for name, f in flags.items():
        idx = g[f.reindex(g).fillna(False).to_numpy(bool)]
        if len(idx) == 0:
            continue
        s = sc.loc[idx]
        out.append(dict(src=grp, flag=name, n=len(idx), base=s.base.mean(), wrong=(s.base < 0.5).mean(),
                        one_reask=s.mean_1alt.mean(), med3=s.med3.mean(), med5=s.med5.mean(),
                        verify=s.verify_final.mean(), oracle3=s.oracle3.mean()))
res = pd.DataFrame(out)
pd.set_option("display.width", 200)
print(res.round(3).to_string(index=False))
res.to_csv(Path(__file__).with_name("val_flag_table.csv"), index=False)
base.join(sc).to_csv(Path(__file__).with_name("val_rows.csv"))

# precision of each flag for "badly wrong" (item < .5) vs base rate, and how many of the wrong rows it catches
print("\nflag precision / recall for base item < 0.5")
wrong = sc.base < 0.5
for name, f in flags.items():
    f = f.fillna(False).astype(bool)
    if f.sum():
        print(f"  {name:16s} n={int(f.sum()):3d} P(wrong|flag)={wrong[f].mean():.2f} recall={wrong[f].sum() / wrong.sum():.2f}"
              f"  (base rate {wrong.mean():.2f})")
