"""Candidate: restore stated sibling values and the leaderboard-confirmed physical scale that the agent build overwrote.

The agent build (research/blind/build_agent_sub.py) protected only the rows of master.pkl's `fact` column. The pre-agent
base also held other values taken from test inputs, and the agent's answers replaced them:
  F  stated sibling values (same object, same quantity, stated as a prior in a sibling clip of the same scene):
     F1 namefam "stated by ..." rows (research/path85_s2sim/out_changes_namefam.csv)
     F2 birdfam "stated family speed" rows (research/path85_s2sim/out_changes_birdfam.csv): 0088-0091 birds, constant speeds
     F3 C1 B_fact / C_readme rows (research/r86/c1/changes_C1.csv): 0012(+seg) bird 1.19 m (0010's prior) and its wingspan at the
        same-clip scale; small bird 0.94 m (0089's prior) in 0088/0090/0091; dragon 0.75 m (0283's prior)
     F4 the same crow asset in 0011/0013 (body length 1.19 m stated by 0010; the base held 1.19 there before the agent)
     F5 PHYSB2 family facts (research/physb2/out/log_physb2.csv): acorn 8 cm (0067's prior) in 0061/0068, cup 10.5 cm
        (0046's prior) in 0069
  P  physical scale of self-filmed internet clips whose stated motion prior is off (PHYSB +.009 D2 and PHYSB2 +.006 D2 on
     the leaderboard): 0053 and 0054 (rider 2.5 / 2.85 m under the stated speed) -> the base's PHYSB values; 0047 (gym ball
     28.9 cm under the stated speed) -> agent x (gym-family ball 24.0 cm / 28.9 cm). 0051 (ambiguous in the PHYSB calibration),
     0043/0045/0055/0069 (the agent already reads the physical scale) stay agent.
  B  0089 distance between the birds at 0.3 s: the base's speed-anchored value (positions follow the stated speeds).
  O  simulation_0020 ball velocity at 0.0 s: agent 123 m/s ("wrap-around backward difference", confidence very low) -> base.
Nothing else changes. No validation or test labels are read.

    .venv/bin/python research/next/nlres/build_svr.py   -> submissions/trackA_cand_next_nlres.csv, research/next/nlres/changes_svr.csv
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "submissions/trackA_probe_agent_sim2agent.csv"
PRE = ROOT / "submissions/trackA_cand_C1_solS2S3.csv"
OUT = ROOT / "submissions/trackA_cand_next_nlres.csv"
LOG = Path(__file__).resolve().parent / "changes_svr.csv"


def col(path):
    d = pd.read_csv(path)
    d = d.rename(columns={d.columns[0]: "id"}).set_index("id")
    return d["parsed_value"].astype(float)


def main():
    best = col(BASE)
    pre = col(PRE)
    t = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
    new: dict[int, tuple[float, str, str]] = {}

    def put(q, v, grp, why):
        q = int(q)
        assert q not in new, f"row {q} set twice"
        new[q] = (float(v), grp, why)

    nf = pd.read_csv(ROOT / "research/path85_s2sim/out_changes_namefam.csv")
    for r in nf[nf.why.str.startswith("stated by")].itertuples():
        put(r.qid, r.new, "F1 namefam", r.why)
    bf = pd.read_csv(ROOT / "research/path85_s2sim/out_changes_birdfam.csv")
    for r in bf[bf.why.str.startswith("stated family speed")].itertuples():
        put(r.qid, r.new, "F2 birdfam speed", r.why)
    c1 = pd.read_csv(ROOT / "research/r86/c1/changes_C1.csv")
    for r in c1[c1.component.isin(["B_fact", "C_readme"])].itertuples():
        put(r.qid, r.new, "F3 C1 fact", r.why)
    # F4: same crow asset (0010 states 'length of the bird = 1.19m'); base held 1.19 before the agent
    prior10 = t.loc[t.video_id.eq("simulation_0010"), "prior"].iloc[0]
    assert "1.19" in prior10, prior10
    for q in (1062, 1065):
        assert "body length of the bird" in t.question[q] and np.isclose(pre[q], 1.19)
        put(q, 1.19, "F4 crow length", "stated by simulation_0010: length of the bird = 1.19m (same asset)")
    p2 = pd.read_csv(ROOT / "research/physb2/out/log_physb2.csv")
    for r in p2[p2.rule.str.startswith("family fact")].itertuples():
        if r.qid in (3196, 3243, 3251):
            put(r.qid, r.new, "F5 PHYSB2 fact", r.rule)
    # P: physical scale
    p1 = pd.read_csv(ROOT / "research/internet/out/log_physb.csv")
    for r in p1.itertuples():
        v = t.video_id[r.qid]
        if v in ("internet_0053", "internet_0054"):
            put(r.qid, pre[r.qid], "P PHYSB", f"base PHYSB value ({r.note})")
    gym = [3102, 3180, 3220, 3228, 3229]                      # ball diameter in same-gym gravity clips 0048/0059/0064/0065/0066
    anchor = float(np.median(best[gym]))
    q47 = t.index[t.video_id.eq("internet_0047")]
    k47 = anchor / best[3096]
    for q in q47:
        put(q, best[q] * k47, "P PHYSB2 0047", f"agent x {k47:.4f} (gym ball {anchor:.1f} cm / 0047 ball {best[3096]:.1f} cm)")
    # B: bird distance at the speed-anchored scale
    put(141, bf.set_index("qid").new[141], "B birdfam distance", "speed-anchored scale (stated family speeds)")
    # O: 0020 velocity at 0.0 s
    put(9, pre[9], "O outlier", "agent 123 m/s (wrap-around guess, very low confidence) -> base")

    out = best.copy()
    rows = []
    for q, (v, grp, why) in sorted(new.items()):
        rows.append(dict(qid=q, video_id=t.video_id[q], category=t.category[q], srcg=t.srcg[q], scored=bool(t.scored[q]),
                         group=grp, old=best[q], new=v, ratio=v / best[q], question=t.question[q], why=why))
        out[q] = v
    log = pd.DataFrame(rows)
    log.to_csv(LOG, index=False)
    ch = log[~np.isclose(log.old, log.new, rtol=1e-9)]
    print(f"rows set {len(log)}, changed {len(ch)}, scored changed {int(ch.scored.sum())}")
    print(ch[ch.scored].groupby(["category", "srcg"]).size().to_string())
    print(ch[ch.scored].groupby(["group"]).size().to_string())
    # never touch a stated-fact row of the base
    is_fact = t.fact.notna() & np.isclose(best.reindex(t.index), t.fact.fillna(-1), rtol=1e-6)
    assert not is_fact.reindex(ch.qid).any(), "a stated-fact row would change"
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        pd.DataFrame({"id": out.index, "parsed_value": out.values}).to_csv(fh, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(OUT)], check=True)
    chk = col(OUT)
    diff = ~np.isclose(chk, best.reindex(chk.index), rtol=1e-9)
    assert set(chk.index[diff]) == set(ch.qid), "unexpected rows differ"
    print("verified: only the logged rows differ from", BASE.name)


if __name__ == "__main__":
    main()
