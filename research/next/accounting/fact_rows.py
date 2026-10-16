"""Stated-fact transfers that build_agent_sub.py did not protect (it protected only master.fact rows).

A non-lab row is a lost fact transfer when
  (a) its pre-agent value (trackA_cand_C1_solS2S3.csv) equals, to 1e-6 (after m<->cm), a number stated in the prior of
      another test clip j, i.e. an earlier family lever (p5 / p7b / path85 / physb2 / C1) set it to j's stated value;
  (b) the question asks the same quantity of the same object that j's prior states: same quantity class
      (size / speed / acceleration) and every content word of the prior's object phrase appears in the question
      ('length of the small bird' -> 'body length of the small bird'); this rejects numeric coincidences
      (whale length 18 vs 'acceleration of the plane = 18', pier length 5 vs 'length of the chalkboard = 5m');
  (c) the current best holds the agent's answer and it differs from the stated value by > 0.5%.
Output: fact_rows.csv (qid, stated value, source clip and prior).  Test inputs only.

    .venv/bin/python research/next/accounting/fact_rows.py
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

from load import master, read, agent_answers, same

NUM = re.compile(r"(\d+(?:\.\d+)?)")
STOP = {"the", "of", "a", "an", "in", "at", "from", "to", "and", "s", "m", "cm", "mm", "is", "what", "moving", "total"}
SIZE = {"length", "height", "width", "diameter", "wingspan", "size", "tall", "long", "wide"}
SPEED = {"speed", "velocity"}
ACC = {"acceleration", "acc"}


def qclass(words):
    w = set(words)
    if w & ACC:
        return "acc"
    if w & SPEED:
        return "speed"
    if w & SIZE:
        return "size"
    return None


def words(s):
    return re.findall(r"[a-z]+", s.lower())


def parse_prior(p):
    """'length of the small bird = 0.94m' -> ('size', {'small','bird'}, 0.94)."""
    out = []
    for part in re.split(r"[;\n]", str(p)):
        if "=" not in part:
            continue
        lhs, rhs = part.split("=", 1)
        m = NUM.search(rhs)
        if not m:
            continue
        lw = words(lhs)
        qc = qclass(lw)
        if qc is None:
            continue
        obj = {w for w in lw if w not in STOP and w not in SIZE | SPEED | ACC | {"body", "average", "maximum"}}
        obj -= {"t", "before", "after"}
        out.append((qc, obj, float(m.group(1))))
    return out


def main():
    t = master()
    cur = read("trackA_probe_agent_sim2agent", t.index)
    pre = read("trackA_cand_C1_solS2S3", t.index)
    ag = agent_answers(t.index, t)
    stated = []  # (clip, qclass, objwords, value, prior)
    for v, p in t.groupby("video_id").prior.first().items():
        for qc, obj, x in parse_prior(p):
            stated.append((v, qc, obj, x, p))
    rows = []
    cand = t.index[t.srcg.ne("lab") & ag.notna() & same(cur, ag.fillna(-1))]
    for i in cand:
        qw = words(t.question[i])
        qc = qclass(qw)
        for (v, sc, obj, x, p) in stated:
            if v == t.video_id[i] or sc != qc or not obj:
                continue
            for mult in (1.0, 100.0, 0.01):
                if np.isclose(pre[i], x * mult, rtol=1e-6) and obj <= set(qw):
                    rows.append(dict(qid=i, video=t.video_id[i], cat=t.category[i], scored=bool(t.scored[i]),
                                     question=t.question[i], stated=x * mult, src=v, src_prior=p, agent=ag[i],
                                     ag_ratio=ag[i] / (x * mult)))
    d = pd.DataFrame(rows).drop_duplicates("qid")
    d = d[(np.log(d.ag_ratio).abs() > np.log(1.005))]
    pd.set_option("display.width", 250, "display.max_colwidth", 60, "display.max_rows", 200)
    print(d.round(4).to_string(index=False))
    print("rows:", len(d), "scored:", int(d.scored.sum()), d[d.scored].groupby(["cat"]).size().to_dict())
    d.to_csv(__file__.replace("fact_rows.py", "fact_rows.csv"), index=False)


if __name__ == "__main__":
    main()
