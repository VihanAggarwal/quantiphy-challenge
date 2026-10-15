"""Does scene-family pooling (qp.postprocess pool rule) help the agentic answers? Held-out check on stated facts.

cur = agent answer where the agent answered (clip types given), else our raw routed answer (never the stated value:
rows whose base equals their stated fact fall back to raw, so no exact fact enters a pool). The pool rule runs
WITHOUT the facts rule (nothing protected); fact rows that the agent answered are then scored before / after.
In a submission, groups holding a stated fact are left to the facts, so this measures pooling quality on the
same kind of groups, not its exact effect.

    .venv/bin/python research/blind/pool_check.py [--root /tmp/blind_test] [--types sim3,internet,sim2]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp import postprocess as pp  # noqa: E402
from qp.data import load_split  # noqa: E402
from qp.mra import item_scores  # noqa: E402


def agent_series(t, root):
    ag = {}
    for f in Path(root).glob("*/answers.json"):
        try:
            for k, x in json.loads(f.read_text()).items():
                try:
                    val = abs(float(x))
                except (TypeError, ValueError):
                    continue
                if np.isfinite(val) and val > 0:
                    ag[(f.parent.name, int(k))] = val
        except json.JSONDecodeError:
            pass
    return pd.Series([ag.get((v, i), np.nan) for i, v in zip(t.index, t.video_id)], index=t.index)


def kinds(t):
    return pd.Series(np.where(t.srcg.eq("sim") & t.video_type.str[1].eq("3"), "sim3",
                              np.where(t.srcg.eq("sim") & t.video_type.str[1].eq("2"), "sim2",
                                       np.where(t.srcg.eq("internet"), "internet", "lab"))), index=t.index)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/tmp/blind_test")
    ap.add_argument("--types", default="sim3,internet,sim2")
    a = ap.parse_args()
    t = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
    kind = kinds(t)
    ans = agent_series(t, a.root)
    # segmented twins take the original's answer (as in build_agent_sub.py)
    orig = {(v, pp.norm_question(q)): i for i, v, q in zip(t.index, t.video_id, t.question) if not v.endswith("_segmented")}
    for i, v, q in zip(t.index, t.video_id, t.question):
        if v.endswith("_segmented") and np.isnan(ans[i]):
            j = orig.get((v[: -len("_segmented")], pp.norm_question(q)))
            if j is not None:
                ans[i] = ans.get(j, np.nan)
    raw = t.r_parsed_value.where(~(t.category.isin(["S3", "D3"]) & t.srcg.eq("sim")), t.dmed)
    use = ans.notna() & kind.isin(a.types.split(","))
    cur = raw.where(raw > 0).copy()
    cur[use] = ans[use]
    cur = cur.dropna()
    test = load_split("test")
    rows = []
    for nm, opt in (("clip tau.15", {}), ("clip median", {"tau": 0.0}), ("clip maxdev1.6", {"max_dev": 1.6}),
                    ("clip mad.1", {"max_mad": 0.1})):
        new, log = pp.apply_rules(cur, test, rules=("pool",), options={"pool": opt})
        new = new.reindex(t.index)
        fm = use & t.fact.notna()
        ch = fm & ~np.isclose(new.fillna(-1), cur.reindex(t.index).fillna(-1))
        s0 = item_scores(cur.reindex(t.index)[fm].to_numpy(), t.fact[fm].to_numpy())
        s1 = item_scores(new[fm].to_numpy(), t.fact[fm].to_numpy())
        d = pd.Series(s1 - s0, index=t.index[fm])
        rows.append(dict(variant=nm, fact_rows=int(fm.sum()), changed=int(ch.sum()), before=s0.mean(), after=s1.mean(),
                         gain_on_changed=d[ch[fm]].mean() if ch.any() else 0.0,
                         pooled_scored_nonfact=int((use & t.scored & t.fact.isna() &
                                                    ~np.isclose(new.fillna(-1), cur.reindex(t.index).fillna(-1))).sum())))
        if nm == "clip tau.15" and ch.any():
            show = pd.DataFrame({"v": t.video_id[ch], "q": t.question[ch].str[:55], "fact": t.fact[ch],
                                 "agent": cur.reindex(t.index)[ch], "pooled": new[ch]})
            print(show.round(3).to_string())
    print(pd.DataFrame(rows).round(4).to_string())


if __name__ == "__main__":
    main()
