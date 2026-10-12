"""Per-rule validation effect of the Track B preset (qp.postprocess.PRESETS['trackb']) on the Track B median:
each rule alone, the preset, and the preset minus each rule; plus test rows changed per rule and category.

    .venv/bin/python research/trackb_rules/per_rule.py"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import CATS, VAL_OFFSET, combined, load_split, median4, pp, score_val  # noqa: E402


def run(pred, df, rules, speed_guard, options):
    return pp.apply_rules(pred, df, rules=tuple(rules), speed_guard=speed_guard,
                          options={k: v for k, v in options.items() if k in rules})


if __name__ == "__main__":
    pre = pp.PRESETS["trackb"]
    df, pred, lab, cat, _ = combined()
    base = score_val(pred, lab, cat)
    rows = []

    def add(name, rules):
        new, log = run(pred, df, rules, pre["speed_guard"], pre["options"])
        s = score_val(new, lab, cat)
        ch = [q for q in lab.index if np.isfinite(pred[q]) and not np.isclose(new[q], pred[q], rtol=1e-9)]
        d = (s["items"] - base["items"])[ch]
        rows.append(dict(config=name, MRA=round(s["MRA"], 4), dMRA=round(s["MRA"] - base["MRA"], 4),
                         **{f"d{c}": round(s[c] - base[c], 4) for c in CATS}, val_rows=len(ch),
                         item_sum=round(d.sum(), 2), better=int((d > 0).sum()), worse=int((d < 0).sum())))
    for r in pp.RULES:
        add(f"{r} alone", [r] if r != "kscale" else ["facts", "kscale"])
    add("v1 (twin, render, facts)", pp.DEFAULT_RULES)
    add("preset trackb", pre["rules"])
    for r in pre["rules"]:
        add(f"preset - {r}", [x for x in pre["rules"] if x != r])
    print(f"raw median4 val MRA {base['MRA']:.4f} " + " ".join(f"{c} {base[c]:.4f}" for c in CATS))
    print(pd.DataFrame(rows).to_string(index=False))
    # test rows changed per rule / category (preset on the test table alone)
    t = load_split("test")
    raw = median4("test", t.qid)
    new, log = run(raw, t, pre["rules"], pre["speed_guard"], pre["options"])
    print("\ntest rows changed by the preset, per rule and category:")
    print(pp.summary(log, t).to_string(index=False))
    ch = ~np.isclose(new, raw, rtol=1e-9) & raw.notna()
    print("total changed per category:", t.set_index("qid").category[ch[ch].index].value_counts().to_dict(),
          "| median |log change|", round(float(np.median(np.abs(np.log(new[ch] / raw[ch])))), 3))
