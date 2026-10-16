"""Stated-fact transfers that are NOT in master.fact (added by levers after master.pkl was built) and that the agent
overwrote.  A row is "fact-like" when its pre-agent value (C1_solS2S3) equals, to 1e-6, a number stated in the prior of
ANOTHER test clip, after unit conversion (m<->cm), and the change log of a lever marks it as a fact transfer.

    .venv/bin/python research/next/accounting/fact_like.py
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

from load import master, read, agent_answers, same, ROOT

NUM = re.compile(r"(\d+(?:\.\d+)?)")


def main():
    t = master()
    cur = read("trackA_probe_agent_sim2agent", t.index)
    pre = read("trackA_cand_C1_solS2S3", t.index)
    ag = agent_answers(t.index, t)
    # numbers stated in priors, by clip
    stated = {}
    for v, p in zip(t.video_id, t.prior):
        for x in NUM.findall(str(p)):
            stated.setdefault(float(x), set()).add(v)
    vals = np.array(sorted(stated))
    rows = []
    for i in t.index[t.srcg.ne("lab") & ag.notna() & same(cur, ag.fillna(-1))]:
        b = pre[i]
        for mult in (1.0, 100.0, 0.01):
            x = b / mult
            k = np.searchsorted(vals, x)
            for kk in (k - 1, k):
                if 0 <= kk < len(vals) and np.isclose(vals[kk], x, rtol=1e-6) and (stated[vals[kk]] - {t.video_id[i]}):
                    rows.append(dict(qid=i, video=t.video_id[i], cat=t.category[i], scored=t.scored[i],
                                     q=t.question[i][:70], pre=b, agent=ag[i], stated=vals[kk], mult=mult,
                                     src=",".join(sorted(stated[vals[kk]] - {t.video_id[i]}))[:60],
                                     fact_col=t.fact[i], prov=t.prov[i]))
    d = pd.DataFrame(rows).drop_duplicates("qid")
    # keep only values that are not trivially round coincidences with raw answers: require pre != raw pipeline answer
    d["raw"] = t.r_parsed_value.reindex(d.qid).values
    d["dmed"] = t.dmed.reindex(d.qid).values
    d["pre_eq_raw"] = np.isclose(d.pre, d.raw, rtol=1e-6) | np.isclose(d.pre, d.dmed, rtol=1e-6)
    d["ag_over_pre"] = d.agent / d.pre
    pd.set_option("display.width", 250, "display.max_colwidth", 70, "display.max_rows", 500)
    print(d.round(4).to_string(index=False))
    d.to_csv(__file__.replace("fact_like.py", "fact_like.csv"), index=False)


if __name__ == "__main__":
    main()
