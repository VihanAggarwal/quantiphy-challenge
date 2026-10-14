"""Validation of the combined candidates (combined table) + rows changed vs the uploaded v3 (scored rows only)."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from harness import CATS, V3, VAL_OFFSET, Data, fmt  # noqa
from levers_a import labnoise  # noqa
from eval_l6s import fb_all  # noqa  (re-runs eval_l6s; cheap enough)
D = Data()
base, _ = D.rules(D.combined(V3))
S = {c: [("qwen_fov" if m == "qwen_geo" and c in ("S3", "D3") else m) for m in v] for c, v in V3.items()}
p, lg = D.rules(D.combined(S))
main, _ = labnoise(D, p, lg, D.df)
pv = D.combined(S)
for q, x in fb_all["test"].dropna().items():
    if q in pv.index:
        pv[q] = x
for q, x in fb_all["val"].dropna().items():
    pv[q + VAL_OFFSET] = x
pp_, lgp = D.rules(pv)
plus, _ = labnoise(D, pp_, lgp, D.df)
ib = D.items(base)
for name, x in (("main L1+L2'", main), ("plus L1+L2'+L6s(+L4: no val rows)", plus)):
    print(name, fmt(D.score(x)), "| boot", fmt(D.boot(base, x)))
    it = D.items(x)
    ch = ~np.isclose(base.reindex(D.lab.index), x.reindex(D.lab.index), rtol=1e-9, equal_nan=True)
    for c in CATS:
        m = ch & (D.vcat == c).to_numpy()
        if m.sum():
            print(f"   val {c}: {int(m.sum())} rows changed, item change per changed row {float((it[m] - ib[m]).mean()):+.3f}")
v3 = pd.read_csv(ROOT / "submissions/trackB_v3_catmedian_famrules.csv").set_index("id").parsed_value
t = D.test.set_index("qid")
for f in ("trackB_cand_v5.csv", "trackB_cand_v5plus.csv"):
    c = pd.read_csv(ROOT / "submissions" / f).set_index("id").parsed_value
    d = pd.Series(~np.isclose(c, v3.reindex(c.index), rtol=1e-9), index=c.index)
    sc = d & ~pd.Series(D.dup, index=D.test.qid).reindex(c.index)
    print(f, "changed rows (all):", t.category[d[d].index].value_counts().to_dict(),
          "| scored (non-val-overlap):", t.category[sc[sc].index].value_counts().to_dict())
