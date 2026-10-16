"""Held-out VALIDATION check of scene-family pooling on top of the agent answers.

The 24 pilot validation clips belong to the same scene families as test clips (often the very same clip id, other
questions). Here the validation questions are appended to the test question table (qid + 100000) with the agent's
validation answers, the test rows carry the agent's test answers (non-lab; segmented twins inherit), and the pool rule
runs exactly as it would in a submission (facts rule first: groups holding a stated fact are protected). Validation
labels are read only to score the validation rows before / after pooling. Nothing here writes a test answer.

    .venv/bin/python research/next/nlres/pool_val.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from qp import postprocess as pp  # noqa: E402
from qp.data import load_split  # noqa: E402
from qp.mra import item_scores  # noqa: E402

OFF = 100000


def main():
    t = pd.read_pickle(ROOT / "research/next/nlres/test_conf.pkl")
    v = pd.read_pickle(ROOT / "research/next/nlres/val_conf.pkl")
    test = load_split("test")
    val = load_split("val_hires")
    val = val.assign(qid=val.qid + OFF)
    both = pd.concat([test, val.drop(columns=["answer"])], ignore_index=True)
    raw = t.r_parsed_value.where(~(t.category.isin(["S3", "D3"]) & t.srcg.eq("sim")), t.dmed)
    cur_t = raw.where(raw > 0).copy()
    nl = t.ctype.ne("lab") & t.agent.notna()
    cur_t[nl] = t.agent[nl]
    vv = v[v.ctype.ne("lab")]
    cur_v = pd.Series(vv.agent.to_numpy(float), index=vv.index + OFF)
    cur = pd.concat([cur_t.dropna(), cur_v.dropna()])
    gt = pd.Series(vv["answer"].astype(float).to_numpy(), index=vv.index + OFF)
    res = []
    base_new, _ = pp.apply_rules(cur, both, rules=("facts",))
    for nm, opt in (("tau.15", {}), ("median", {"tau": 0.0}), ("maxdev1.6", {"max_dev": 1.6}), ("mad.1", {"max_mad": 0.1}),
                    ("base-unit maxdev1.6", {"unit": "base", "max_dev": 1.6})):
        new, log = pp.apply_rules(cur, both, rules=("facts", "pool"), options={"pool": opt})
        b = base_new.reindex(gt.index)
        a = new.reindex(gt.index)
        ch = ~np.isclose(a.fillna(-1), b.fillna(-1))
        s0 = pd.Series(np.nan_to_num(item_scores(b.to_numpy(), gt.to_numpy())), index=gt.index)
        s1 = pd.Series(np.nan_to_num(item_scores(a.to_numpy(), gt.to_numpy())), index=gt.index)
        tch = new.reindex(t.index)
        tb = base_new.reindex(t.index)
        tchg = t.scored & ~t.ctype.eq("lab") & ~np.isclose(tch.fillna(-1), tb.fillna(-1))
        res.append(dict(variant=nm, val_rows=len(gt), val_changed=int(ch.sum()), before=s0.mean(), after=s1.mean(),
                        gain_on_changed=(s1 - s0)[ch].mean() if ch.any() else 0.0,
                        test_scored_nonlab_changed=int(tchg.sum()),
                        test_by_cat=t.loc[tchg].category.value_counts().to_dict()))
        if nm == "tau.15" and ch.any():
            idx = gt.index[ch]
            show = pd.DataFrame({"video": vv.video_id.reindex(idx - OFF).to_numpy(), "q": vv.question.reindex(idx - OFF).str[:55].to_numpy(),
                                 "gt": gt[idx].to_numpy(), "agent": b[idx].to_numpy(), "pooled": a[idx].to_numpy(),
                                 "s0": s0[idx].to_numpy(), "s1": s1[idx].to_numpy()}, index=idx - OFF)
            print(show.round(3).to_string())
    print(pd.DataFrame(res).round(4).to_string())


if __name__ == "__main__":
    main()
