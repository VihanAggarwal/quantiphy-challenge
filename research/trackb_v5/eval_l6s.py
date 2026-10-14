"""L6s (POST-HOC, defined after L6 failed): L6 restricted to simulation twins (Blender re-renders; the internet
segmented clips carry the "Modified with Segment Anything 2 Demo" watermark, i.e. approximate SAM 2 demo masks).
a: cv_geo member -> snapped geometry (S2, D2); b: snapped geometry alone on those rows."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "trackb_dense"))
from harness import CATS, V3, VAL_OFFSET, Data, fmt  # noqa: E402
from levers_a import affected_val, changed_rows  # noqa: E402
from tbcommon import specs as load_specs, with_fallback  # noqa: E402
from qp.mra import item_scores  # noqa: E402

D = Data()
fb_all = {}
for split in ("val", "test"):
    R = pd.read_csv(HERE / f"out_{split}_cvq_seg.csv")
    R = R[R.video_id.str.startswith("simulation")].set_index("id")
    frame = D.test if split == "test" else D.val
    sp = load_specs(split)
    kinds = pd.Series({q: sp[q].target.kind for q in R.index if q in sp})
    caw = pd.Series(D.P[split]["caw"].to_numpy(), index=frame.qid)
    fb_all[split] = with_fallback(R.geo_value, R.geo_si, kinds, caw.reindex(R.index))
    base = pd.Series(D.P[split]["cv_geo"].to_numpy(), index=frame.qid)
    base.loc[fb_all[split].index] = fb_all[split].to_numpy()
    fb_all[split + "_m"] = base
D.add_method("cv_seg", fb_all["test_m"], fb_all["val_m"])
S = {c: [("cv_seg" if x == "cv_geo" and c in ("S2", "D2") else x) for x in v] for c, v in V3.items()}
base, _ = D.rules(D.combined(V3))
pa, lga = D.rules(D.combined(S))
pv = D.combined(V3)
for q, x in fb_all["test"].dropna().items():
    if q in pv.index:
        pv[q] = x
for q, x in fb_all["val"].dropna().items():
    pv[q + VAL_OFFSET] = x
pb, lgb = D.rules(pv)
fl = pd.read_csv(HERE.parents[0] / "trackb_dense/out/fact_labels.csv", index_col=0)
fl = fl[fl.index < VAL_OFFSET].lab
r0 = D.raw(V3, "test").reindex(fl.index)
i0 = item_scores(r0.to_numpy(float), fl.to_numpy(float))
for name, p, raw in (("L6s-a member", pa, D.raw(S, "test")), ("L6s-b alone", pb, None)):
    n, s = affected_val(D, base, p)
    print(name, fmt(D.score(p)), "| boot", fmt(D.boot(base, p)), f"| val rows {n} item sum {s:+.3f}",
          f"| test rows {changed_rows(D, base, p)}")
    if raw is None:
        raw = r0.copy()
        for q, x in fb_all["test"].dropna().items():
            if q in raw.index:
                raw[q] = x
    r1 = raw.reindex(fl.index)
    ch = ~np.isclose(r0, r1, rtol=1e-9, equal_nan=True)
    i1 = item_scores(r1.to_numpy(float), fl.to_numpy(float))
    print(f"   facts: changed {int(ch.sum())}, item {np.nanmean(i0[ch]):.3f} -> {np.nanmean(i1[ch]):.3f}")
pd.to_pickle(dict(pa=pa, pb=pb, la=lga, lb=lgb), HERE / "cache_l6s.pkl")
