"""Score fixed (not searched) per-category member sets on validation: v3 and principled substitutions."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from select_sets import V3, all_methods  # noqa: E402
from tbcommon import CATS, item, log_median, questions  # noqa: E402

SUB = {"qwen_geo": "qwen_dense", "cv_geo": "cv_labfov"}


def sets_variants():
    out = {"v3": V3}
    out["v3 sub(dense,cvfov)"] = {c: [SUB.get(m, m) for m in v] for c, v in V3.items()}
    out["v3 sub(dyn,cvfov)"] = {c: [{"qwen_geo": "qwen_dyn", "cv_geo": "cv_labfov"}.get(m, m) for m in v] for c, v in V3.items()}
    out["v3 +hybrid_nopick"] = {c: v + ["hybrid_nopick"] for c, v in V3.items()}
    out["v3 +hybrid"] = {c: v + ["hybrid"] for c, v in V3.items()}
    out["v3 sub +hybrid_nopick"] = {c: [SUB.get(m, m) for m in v] + ["hybrid_nopick"] for c, v in V3.items()}
    out["v3 sub +hybrid"] = {c: [SUB.get(m, m) for m in v] + ["hybrid"] for c, v in V3.items()}
    allm = ["qwen_direct", "caw", "qwen_dense", "cv_labfov", "hybrid_nopick"]
    out["all5"] = {c: allm for c in CATS}
    out["all5+dyn"] = {c: allm + ["qwen_dyn"] for c in CATS}
    out["4: caw,qd,qdense,cvfov"] = {c: ["caw", "qwen_direct", "qwen_dense", "cv_labfov"] for c in CATS}
    return out


if __name__ == "__main__":
    val = questions("val")
    P = all_methods("val", val)
    rows = {}
    for name, sets in sets_variants().items():
        r = {}
        for c in CATS:
            m = (val.category == c).to_numpy()
            r[c] = item(log_median([P[x] for x in sets[c]]), val.answer)[m].mean()
        r["MRA"] = np.mean([r[c] for c in CATS])
        rows[name] = r
    print(pd.DataFrame(rows).T.round(4).to_string())
