"""Expected test (leaderboard) effect of the Track B preset, from test inputs only.

Stated-value rows (facts, motionfam, freefall, labfacts) are scored 'if right' (the stated value taken as the label:
7/7 exact on validation and 5/5 in Track A), i.e. gain = 1 - item(old answer, stated value). Pool rows get a range
per changed row from the label-free stated-fact check (eval_facts.py) and validation. N = scored rows per category
(PROBES.md: S2 553, D2 1137, S3 538, D3 933).

    .venv/bin/python research/trackb_rules/expected.py"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import CATS, ROOT, load_split, median4, pp  # noqa: E402
from qp.mra import item_scores  # noqa: E402

N = {"S2": 553, "D2": 1137, "S3": 538, "D3": 933}
POOL_GAIN = (0.0, 0.04, 0.08)    # per changed pool row: LOVO-validation ~0, validation in-sample, stated-fact check

if __name__ == "__main__":
    t = load_split("test")
    T = t.set_index("qid")
    raw = median4("test", t.qid)
    v1 = pd.read_csv(ROOT / "submissions/trackB_v1_median4_post.csv").set_index("id").parsed_value.reindex(t.qid)
    pre = pp.PRESETS["trackb"]
    new, log = pp.apply_rules(raw, t, rules=pre["rules"], speed_guard=pre["speed_guard"], options=pre["options"])
    L = log[log.applied].drop_duplicates("qid", keep="last").set_index("qid")
    L["cat"] = T.category.reindex(L.index)
    fact = L[L.rule.isin(["facts", "motionfam", "freefall", "labfacts"])]
    g_raw = 1 - item_scores(raw.reindex(fact.index).to_numpy(), fact.new.to_numpy())
    g_v1 = item_scores(fact.new.to_numpy(), fact.new.to_numpy()) - item_scores(v1.reindex(fact.index).to_numpy(), fact.new.to_numpy())
    fact = fact.assign(g_raw=g_raw, g_v1=g_v1)
    pool = L[L.rule == "pool"]
    print("stated-value rows (if right), category points vs raw median / vs v1:")
    tot = {}
    for c in CATS:
        f = fact[fact.cat == c]
        n_pool = int((pool.cat == c).sum())
        tot[c] = (f.g_raw.sum() / N[c], f.g_v1.sum() / N[c], n_pool)
        print(f"  {c}: {len(f):3d} rows  vs raw {tot[c][0]:+.4f}  vs v1 {tot[c][1]:+.4f} | pool rows {n_pool} -> "
              + " / ".join(f"{n_pool * g / N[c]:+.4f}" for g in POOL_GAIN))
    fr = np.mean([tot[c][0] for c in CATS]); fv = np.mean([tot[c][1] for c in CATS])
    pr = [np.mean([tot[c][2] * g / N[c] for c in CATS]) for g in POOL_GAIN]
    print(f"overall: stated values vs raw {fr:+.4f}, vs v1 {fv:+.4f}; pool {pr[0]:+.4f} / {pr[1]:+.4f} / {pr[2]:+.4f}")
    # rows where v1's twin/render copies are undone by v2
    d = pd.Series(~np.isclose(v1, new.reindex(t.qid).fillna(1.0), rtol=1e-9), index=t.qid)
    print("rows differing from v1:", T.category[d[d].index].value_counts().to_dict(), int(d.sum()))
