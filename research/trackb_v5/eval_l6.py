"""L6 evaluation: on 2D rows of segmented clips / originals with a frame-aligned twin, the cv_geo member is replaced
by the mask-snapped cvq geometry (seg_snap.py; CaW fallback as run_open_vlm). Primary variant fixed before scoring.
Secondary (reported only): those rows answered by the snapped geometry alone."""
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
new = {}
for split in ("val", "test"):
    R = pd.read_csv(HERE / f"out_{split}_cvq_seg.csv").set_index("id")
    frame = D.test if split == "test" else D.val
    sp = load_specs(split)
    kinds = pd.Series({q: sp[q].target.kind for q in R.index if q in sp})
    caw = pd.Series(D.P[split]["caw"].to_numpy(), index=frame.qid)
    fb = with_fallback(R.geo_value, R.geo_si, kinds, caw.reindex(R.index))
    base = pd.Series(D.P[split]["cv_geo"].to_numpy(), index=frame.qid)
    m = base.copy(); m.loc[fb.index] = fb.to_numpy()
    alone = pd.Series(np.nan, index=frame.qid); alone.loc[fb.index] = fb.to_numpy()
    new[split] = (m, alone, fb.index)
D.add_method("cv_seg", new["test"][0], new["val"][0])
S = {c: [("cv_seg" if x == "cv_geo" and c in ("S2", "D2") else x) for x in v] for c, v in V3.items()}
base, blog = D.rules(D.combined(V3))
p, lg = D.rules(D.combined(S))
n, s = affected_val(D, base, p)
print("L6 cv_geo->snapped (S2,D2):", fmt(D.score(p)), "| boot", fmt(D.boot(base, p)), f"| val rows {n} item sum {s:+.3f}",
      f"| test rows {changed_rows(D, base, p)}")
# facts: raw sets before rules
fl = pd.read_csv(HERE.parents[0] / "trackb_dense/out/fact_labels.csv", index_col=0)
fl = fl[fl.index < VAL_OFFSET].lab
r0, r1 = D.raw(V3, "test").reindex(fl.index), D.raw(S, "test").reindex(fl.index)
ch = ~np.isclose(r0, r1, rtol=1e-9, equal_nan=True)
i0, i1 = item_scores(r0.to_numpy(float), fl.to_numpy(float)), item_scores(r1.to_numpy(float), fl.to_numpy(float))
print(f"facts: changed {int(ch.sum())} rows, mean item {np.nanmean(i0[ch]):.3f} -> {np.nanmean(i1[ch]):.3f}")
# secondary: snapped geometry alone on affected rows
alone_t, alone_v = new["test"][1], new["val"][1]
pv = D.combined(V3)
for q, x in alone_t.dropna().items():
    if q in pv.index:
        pv[q] = x
for q, x in alone_v.dropna().items():
    pv[q + VAL_OFFSET] = x
p2, _ = D.rules(pv)
n, s = affected_val(D, base, p2)
print("L6b snapped alone:", fmt(D.score(p2)), f"| val rows {n} item sum {s:+.3f}")
a = alone_t.reindex(fl.index)
ch = a.notna().to_numpy()
i2 = item_scores(a.to_numpy(float), fl.to_numpy(float))
print(f"facts alone: rows {int(ch.sum())}, item {np.nanmean(i0[ch]):.3f} -> {np.nanmean(i2[ch]):.3f}")
pd.to_pickle(dict(post=p, log=lg), HERE / "cache_l6.pkl")
