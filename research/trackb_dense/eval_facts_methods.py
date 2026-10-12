"""Label-free check on TEST: score each method / median set on the stated-fact rows (a value another clip of the
scene family states as its prior; research/trackb_rules/eval_facts.py's fact_labels, exact by construction).
These rows get the stated value in the submission anyway (facts rule), but they measure how well each method
answers questions about the same scenes. Validation-overlap rows are excluded.

    .venv/bin/python research/trackb_dense/eval_facts_methods.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from select_sets import V3, all_methods  # noqa: E402
from tbcommon import CATS, OUT, ROOT, item, log_median, questions  # noqa: E402


def fact_labels() -> pd.Series:
    f = OUT / "fact_labels.csv"
    if not f.exists():
        sys.path.insert(0, str(ROOT / "research" / "trackb_rules"))
        from common import combined  # noqa: E402
        from eval_facts import fact_labels as fl  # noqa: E402
        df, pred, _, _, _ = combined()
        L = fl(df, pred)
        T = df.set_index("qid")
        pd.DataFrame({"lab": L, "cat": T.category.reindex(L.index)}).to_csv(f)
    d = pd.read_csv(f, index_col=0)
    return d.lab[d.index < 100000]          # test rows only (validation rows are offset by 100000)


def table(sets: dict[str, dict], P: dict, test: pd.DataFrame, lab: pd.Series) -> pd.DataFrame:
    t = test.set_index("qid")
    cat = t.category.reindex(lab.index)
    rows = {}
    for m, p in P.items():
        s = item(pd.Series(p.to_numpy(), index=test.qid).reindex(lab.index), lab)
        rows[m] = {c: s[cat == c].mean() for c in CATS} | {"all": s.mean()}
    for name, st in sets.items():
        pred = pd.Series(np.nan, index=test.qid)
        for c in CATS:
            m = (test.category == c).to_numpy()
            pred[m] = log_median([P[x] for x in st[c]])[m].to_numpy()
        s = item(pred.reindex(lab.index), lab)
        rows["SET " + name] = {c: s[cat == c].mean() for c in CATS} | {"all": s.mean()}
    out = pd.DataFrame(rows).T
    out.loc["n"] = [int((cat == c).sum()) for c in CATS] + [len(lab)]
    return out


if __name__ == "__main__":
    test = questions("test")
    lab = fact_labels()
    P = all_methods("test", test)
    print(table({"v3": V3}, P, test, lab).round(3).to_string())
