"""Per-rule validation effect of the extended qp.postprocess rules on the Track B median answers.

    .venv/bin/python research/trackb_rules/eval_rules.py

Each configuration runs on the combined question table (test + validation, research/trackb_rules/common.py);
only validation rows are scored, with labels read here and never passed to the rules."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import CATS, VAL_OFFSET, combined, pp, score_val  # noqa: E402


def run(df, pred, lab, cat, rules, options=None, show=False):
    new, log = pp.apply_rules(pred, df, rules=tuple(rules), options=options or {})
    s = score_val(new, lab, cat)
    return new, log, s


def changed_val(new, pred, lab):
    return [q for q in lab.index if np.isfinite(pred[q]) and not np.isclose(new[q], pred[q], rtol=1e-9)]


if __name__ == "__main__":
    df, pred, lab, cat, ndup = combined()
    T = df.set_index("qid")
    base = score_val(pred, lab, cat)
    print(f"combined table {len(df)} rows ({ndup} test rows repeating a validation question dropped)")
    print("raw median4: " + " ".join(f"{k} {base[k]:.4f}" for k in ("MRA",) + CATS))
    configs = sys.argv[1:] or ["facts", "render", "twin", "motionfam", "freefall", "labfacts", "facts,kscale",
                               "pool", "labpool", "facts,motionfam,freefall,labfacts,kscale,pool,labpool"]
    for c in configs:
        rules = c.split(",")
        new, log, s = run(df, pred, lab, cat, rules)
        ch = changed_val(new, pred, lab)
        d = (s["items"] - base["items"])[ch]
        nt = int((~np.isclose(new.drop(lab.index), pred.drop(lab.index), rtol=1e-9) & pred.drop(lab.index).notna()).sum())
        print(f"{c:60s} MRA {s['MRA']:.4f} ({s['MRA'] - base['MRA']:+.4f}) " +
              " ".join(f"{k} {s[k] - base[k]:+.4f}" for k in CATS) +
              f" | val rows changed {len(ch)} (item sum {d.sum():+.1f}; better {int((d > 0).sum())}, worse {int((d < 0).sum())}) | test rows changed {nt}")
        if "-v" in c or len(sys.argv) > 1:
            for q in ch:
                print(f"     {q - VAL_OFFSET} {cat[q]} {T.loc[q, 'video_id']:28s} {T.loc[q, 'question'][:70]:70s} "
                      f"{pred[q]:.4g} -> {new[q]:.4g} gt {lab[q]:.4g}  {base['items'][q]:.1f}->{s['items'][q]:.1f}")
