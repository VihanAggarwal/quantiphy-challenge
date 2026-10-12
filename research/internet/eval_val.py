"""Validation check of the FWD rule (labels used for evaluation only): internet rows of val_hires replayed with
the forward-difference emulation off / on (research/internet/fwd_emulate.py --split val_hires --run val_hr_v1_high)."""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp.mra import item_scores  # noqa: E402

v = pd.read_csv(ROOT / "data/QuantiPhy-validation/validation_dataset.csv")
o = ROOT / "research/internet/out"
off = pd.read_csv(o / "val_hires_val_hr_v1_high_fwd1_off.csv")
on = pd.read_csv(o / "val_hires_val_hr_v1_high_fwd1_on.csv")
m = v.merge(off[["id", "geo_value"]], left_on="Unnamed: 0", right_on="id") \
     .merge(on[["id", "geo_value"]].rename(columns={"geo_value": "g1"}), on="id")
m["s0"], m["s1"] = item_scores(m.geo_value, m.ground_truth_posterior), item_scores(m.g1, m.ground_truth_posterior)
x = m[(m.g1 / m.geo_value - 1).abs() > 0.002].copy()
x["logerr_off"] = np.log(x.geo_value / x.ground_truth_posterior)
x["logerr_on"] = np.log(x.g1 / x.ground_truth_posterior)
print(x[["video_id", "question", "ground_truth_posterior", "geo_value", "g1", "logerr_off", "logerr_on", "s0", "s1"]]
      .to_string(index=False))
print(f"internet rows {len(m)}: MRA off {m.s0.mean():.4f} on {m.s1.mean():.4f}; changed {len(x)}; "
      f"mean |log err| {x.logerr_off.abs().mean():.4f} -> {x.logerr_on.abs().mean():.4f}")
