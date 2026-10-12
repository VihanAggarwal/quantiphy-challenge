"""Leave-one-video-out (LOVO) check of the rule-configuration choice on validation (Track B median answers).

Every configuration in GRID runs once on the combined test + validation question table (labels never enter the
rules). For each of the 24 validation videos, the configuration with the best validation MRA on the OTHER 23
videos is chosen and its answers are scored on the held-out video; the LOVO MRA is the category macro of those
held-out scores. Compared with the configuration picked on all videos (in-sample) and with fixed configurations.

    .venv/bin/python research/trackb_rules/lovo.py
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import CATS, combined, pp, score_val  # noqa: E402

FACTS = ("facts", "motionfam", "freefall", "labfacts")


def grid():
    out = {"raw": ((), {}), "v1 (facts,render,twin)": (("facts", "render", "twin"), {}),
           "facts+": (FACTS, {})}
    for unit, dev, tau in itertools.product(("clip", "base"), (None, 1.6, 2.0), (0.15, 0.0)):
        o = {"pool": {"unit": unit, "max_dev": dev, "tau": tau}}
        tag = f"pool[{unit},dev={dev},tau={tau}]"
        out[f"facts+ {tag}"] = (FACTS + ("pool",), o)
        out[f"facts+ {tag} +labpool"] = (FACTS + ("pool", "labpool"), o)
    out["facts+ kscale pool[base,1.6]"] = (FACTS + ("kscale", "pool"), {"pool": {"unit": "base", "max_dev": 1.6}})
    out["facts+ pool[base,1.6] render"] = (FACTS + ("pool", "render"), {"pool": {"unit": "base", "max_dev": 1.6}})
    out["facts+ pool[base,1.6] render twin"] = (FACTS + ("pool", "render", "twin"),
                                                {"pool": {"unit": "base", "max_dev": 1.6}})
    return out


def macro(items, cat):
    return float(np.mean([items[cat == c].mean() for c in CATS if (cat == c).any()]))


if __name__ == "__main__":
    df, pred, lab, cat, _ = combined()
    vid = df.set_index("qid").video_id.reindex(lab.index)
    G = grid()
    items = {}
    for name, (rules, opts) in G.items():
        new, _ = pp.apply_rules(pred, df, rules=rules, options=opts)
        items[name] = score_val(new, lab, cat)["items"]
        print(f"{name:55s} val MRA {macro(items[name], cat):.4f}", flush=True)
    I = pd.DataFrame(items)
    held = pd.Series(np.nan, index=lab.index)
    picks = {}
    for v in vid.unique():
        m = (vid == v).to_numpy()
        tr = I[~m]
        best = max(I.columns, key=lambda c: macro(tr[c], cat[~m]))
        picks[v] = best
        held[m] = I.loc[m, best]
    print(f"\nLOVO choice over {len(G)} configurations: val MRA {macro(held, cat):.4f} "
          f"(raw {macro(I['raw'], cat):.4f}, v1 {macro(I['v1 (facts,render,twin)'], cat):.4f}, "
          f"in-sample best {max(macro(I[c], cat) for c in I):.4f})")
    print("picks:", json.dumps(pd.Series(picks).value_counts().to_dict(), indent=1))
