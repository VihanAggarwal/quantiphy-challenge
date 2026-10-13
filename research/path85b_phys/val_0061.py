"""Out-of-sample check of the constant-g lab fit on validation clip captured_0061 (labels read for scoring only;
method fixed beforehand: g = 9.8, f = 722, capture clock with dropped frames, forward difference at 25 fps)."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent)); sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import labfit as L
from qp.mra import item_scores
from qp.data import load_validation
ROOT = Path(__file__).resolve().parents[2]
dd = json.loads((ROOT / "runs/_dense_cache/val/captured_0061.json").read_text())
P = {k[:6]: {int(f): tuple(v) for f, v in e["path"].items()} for k, e in dd.items() if e.get("path")}
segs = {  # question time -> (path, frames, ranges)
    0.6: ("6117ed", 8, 26, [(0.6, 1.937), (0.9, 1.585)]),
    0.9: ("6117ed", 8, 26, [(0.6, 1.937), (0.9, 1.585)]),
    1.1: ("2d4948", 24, 30, [(1.1, 2.42)]),
    1.6: ("2d4948", 31, 48, [(1.6, 1.9015)]),
}
v = load_validation(); v = v[v.video_id == "captured_0061"].set_index("qid")
qmap = {0.6: 3052, 0.9: 3053, 1.1: 3054, 1.6: 3055}
comb = pd.read_csv(ROOT / "submissions/trackA_cand_path85_combo.csv").set_index("id").parsed_value
cur = {0.6: [2905, 2912, 2919], 0.9: [2906, 2913, 2920], 1.1: [2907, 2914, 2921], 1.6: [2908, 2915, 2922]}
rows = []
for t, (k, f0, f1, rng) in segs.items():
    tau, uv, fr = L.segment(P[k], f0, f1)
    fg = L.Fit(tau, uv, rng); ff = L.Fit(tau, uv, rng, free_g=True)
    rows.append(dict(t=t, fit_fd=fg.speed_fd(t), fit_inst=fg.speed_inst(t), free_fd=ff.speed_fd(t),
                     g_free=np.linalg.norm(ff.G()), rms=fg.rms_px, combo_s_x=np.mean([comb[q] for q in cur[t][1:]]),
                     label=v.loc[qmap[t], "answer"]))
R = pd.DataFrame(rows)
for c in ("fit_fd", "fit_inst", "free_fd", "combo_s_x"):
    R["s_" + c] = item_scores(R[c], R.label)
print(R.round(3).to_string())
print(R[[c for c in R if c.startswith("s_")]].mean().round(3).to_string())
