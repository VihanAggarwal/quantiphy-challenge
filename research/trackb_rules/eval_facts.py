"""Label-free check of the pooling / scale rules on stated facts (test inputs only).

Rows that a scene family STATES (the facts rule's applied rows, exact labels by the same procedure) are scored with
the facts rule OFF, so the stated value is held out of every rule (leave-one-fact-out, as the Track A study did).
Usage: .venv/bin/python research/trackb_rules/eval_facts.py ["rules;json-options" ...]"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import VAL_OFFSET, combined, pp  # noqa: E402
from qp.mra import item_scores  # noqa: E402


def fact_labels(df, pred):
    _, log = pp.apply_rules(pred, df, rules=("facts",), speed_guard=0)
    f = log[log.applied]
    return pd.Series(f.new.to_numpy(float), index=f.qid.astype(int))


def evaluate(df, pred, labels, rules, options=None):
    rules = tuple(r for r in rules if r != "facts")
    new, log = pp.apply_rules(pred, df, rules=rules, options=options or {})
    T = df.set_index("qid")
    a = item_scores(pred.reindex(labels.index).to_numpy(), labels.to_numpy())
    b = item_scores(new.reindex(labels.index).to_numpy(), labels.to_numpy())
    r = pd.DataFrame({"raw": a, "new": b, "cat": T.category.reindex(labels.index).to_numpy()}, index=labels.index)
    r["changed"] = ~np.isclose(new.reindex(labels.index), pred.reindex(labels.index), rtol=1e-9)
    return r


if __name__ == "__main__":
    df, pred, _, _, _ = combined()
    labels = fact_labels(df, pred)
    print(f"{len(labels)} stated-fact rows ({(labels.index >= VAL_OFFSET).sum()} validation)")
    for arg in sys.argv[1:]:
        rules, _, opts = arg.partition(";")
        r = evaluate(df, pred, labels, rules.split(","), json.loads(opts) if opts else None)
        c = r[r.changed]
        by = r.groupby("cat")[["raw", "new"]].mean().round(3)
        print(f"{arg:70s} all {r.raw.mean():.3f}->{r.new.mean():.3f}  changed {len(c)}: {c.raw.mean():.3f}->{c.new.mean():.3f} "
              f"(better {(c.new > c.raw).sum()}, worse {(c.new < c.raw).sum()}) | " +
              " ".join(f"{k} {v.raw:.2f}->{v.new:.2f}" for k, v in by.iterrows()))
