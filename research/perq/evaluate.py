"""Kill test for one-question-per-request (pilot on the 52 validation questions of 3D non-lab clips).

Pass rule (fixed before the run): the per-question run's direct answers beat the matching single batched run
(val_hr_v1_high: same model, effort, frames, resolution, prompt) by >= +0.015 MRA, and win on most of the 6 clips.
Also reported: other single batched runs, the 3-run median, and a median that adds the per-question run.

    .venv/bin/python research/perq/evaluate.py
"""
import glob
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp.data import load_split  # noqa: E402
from qp.mra import item_scores  # noqa: E402

v = load_split("val_hires").set_index("qid")
m = (v.video_type.str[1] == "3") & (v.video_source != "lab")
gt = v.answer[m].astype(float)
vid = v.video_id[m].str.replace("_segmented", "", regex=False)


def direct(path):
    d = pd.read_csv(path).set_index("id")
    return pd.to_numeric(d.direct_value, errors="coerce").reindex(gt.index)


perq_csv = sorted(glob.glob(str(ROOT / "runs/val_perq_high/*.csv")))
if not perq_csv:
    raise SystemExit("no per-question results yet")
runs = {
    "perq_v1_high": direct(perq_csv[0]),
    "batched_hr_v1_high": direct(ROOT / "runs/val_hr_v1_high/val_hires.csv"),
    "batched_hr_v2_high": direct(ROOT / "runs/val_hr_v2_high/val_hires.csv"),
    "batched_opus_high": direct(ROOT / "runs/val_opus_high/val.csv"),
}
L = np.log(pd.DataFrame({k: runs[k] for k in ("batched_hr_v1_high", "batched_hr_v2_high", "batched_opus_high")}))
runs["batched_3run_median"] = np.exp(L.median(axis=1))
L4 = np.log(pd.DataFrame({k: runs[k] for k in ("perq_v1_high", "batched_hr_v2_high", "batched_opus_high")}))
runs["median_perq+2batched"] = np.exp(L4.median(axis=1))

S = pd.DataFrame({k: np.nan_to_num(item_scores(s.to_numpy(), gt.to_numpy()), nan=0.0) for k, s in runs.items()},
                 index=gt.index)
print(f"n={len(S)} questions, {vid.nunique()} clips; answered by perq: {int(runs['perq_v1_high'].notna().sum())}")
print(S.mean().round(4).to_string())
d = S.perq_v1_high - S.batched_hr_v1_high
byclip = d.groupby(vid).mean()
print("\nper clip (perq - batched_hr_v1_high):", byclip.round(3).to_dict())
rng = np.random.default_rng(0)
clips = byclip.index.to_numpy()
bs = []
for _ in range(4000):
    k = rng.choice(clips, len(clips))
    bs.append(np.mean(np.concatenate([d[vid == c].to_numpy() for c in k])))
print(f"delta {d.mean():+.4f}  clip-bootstrap 90% [{np.percentile(bs, 5):+.4f}, {np.percentile(bs, 95):+.4f}]  "
      f"clips better {int((byclip > 0).sum())}/{len(byclip)}")
ok = d.mean() >= 0.015 and (byclip > 0).sum() > len(byclip) / 2
print("KILL TEST:", "PASS" if ok else "FAIL")
