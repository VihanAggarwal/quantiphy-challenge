"""Validation (labels for EVALUATION ONLY): internet clips whose container fps differs from the dataset fps.
For each clip: scale ratio s = median(label/pred) over static rows (sizes, distances) of the v1-high val_hires run;
for motion rows (speed/velocity) the scale-normalised ratio r = label / (pred / s) under the dataset fps (dfps) and
under the container fps (cfps: pred x cfps/dfps for speeds; gravity-scaled clips x (dfps/cfps)^2 for every row)."""
import sys; sys.path.insert(0, '.')
import cv2, numpy as np, pandas as pd
from qp.data import load_validation
v = load_validation(); r = pd.read_csv("runs/val_hr_v1_high/val_hires.csv").set_index("id")
v["pred"] = v.qid.map(r.parsed_value)
for vid, g in v[v.video_id.str.startswith("internet")].groupby("video_id"):
    cap = cv2.VideoCapture(f"data/QuantiPhy/{vid}.mp4"); cfps = cap.get(5); dfps = g.fps.iloc[0]
    if abs(cfps / dfps - 1) < 0.02:
        continue
    mot = g.question.str.contains("speed|veloc", case=False)
    grav = "grav" in g.prior.iloc[0].lower()
    s = np.median(g.answer[~mot] / g.pred[~mot])
    print(f"{vid}: dfps {dfps} cfps {cfps:.3f} prior '{g.prior.iloc[0]}'  static label/pred median {s:.3f} (n={int((~mot).sum())})")
    if grav:
        print(f"   gravity scale under cfps would be x{(dfps/cfps)**2:.3f} -> static label/pred {s/(dfps/cfps)**2:.3f}")
    for _, x in g[mot].iterrows():
        rd = x.answer / (x.pred * s)   # label / (prediction corrected by the clip's static scale ratio)
        rc = (x.answer / (x.pred * (cfps / dfps) * s)) if not grav else float('nan')  # gravity: static rows already rule cfps out
        print(f"   {x.question[:70]:70s} label {x.answer:7.3f} pred {x.pred:7.3f}  r(dfps)={rd:.3f}  r(cfps)={rc:.3f}")
