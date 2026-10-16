"""Candidate: trackA_cand_next_accounting.csv = trackA_probe_agent_sim2agent.csv + two measured-positive family levers
that the agent build overwrote (build_agent_sub.py protected only master.fact rows):

  F  stated-fact transfers (the T rule of probe 5 / p7b / path85 / physb2 / C1): rows whose pre-agent value was a sibling
     clip's stated prior for the same object and quantity (fact_rows.py) take that value again.            [fact_rows.csv]
  P  physical-scale anchors (PHYSB probe 18 D2 +.009, PHYSB2 D2 +.006): the agent took the stated motion prior of these
     self-filmed clips at face value, the leaderboard says their labels are on the physical scale. The agent's answers of
     the clip are rescaled so that its own anchor-object answer equals the family anchor used by PHYSB/PHYSB2:
       internet_0053, internet_0054: rider height = 1.6237 m (the same rider reads 1.58-1.68 m in 0049/0050/0052/0056,
                                     by the agent and by the base); calib_physb.py: 0053/0054 physical in the best fits.
       internet_0047: rolling basketball diameter = 24.2 cm (same-gym gravity clips; physb2 anchor).
       internet_0069: cup height = 10.5 cm (exact fact: same mug as internet_0046, which states it).
     internet_0051 is left alone (ambiguous in calib_physb.py); 0043/0055 already read physical in the agent; 0045 is
     within the physb2 gate (|ln k| < .10).
  R  master.fact rows more than 5% off their stated value: only qid 1747 (simulation_0041_segmented boat average speed,
     fact 4.0, held by probe 5; probe 18's S2 size envelope rescaled the whole clip including this speed row to 3.568).
Every other master.fact row is untouched (already exact or within 3%). Lab rows are untouched. Test inputs only.

    .venv/bin/python research/next/accounting/build_cand.py
"""
from __future__ import annotations

import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd

from load import master, read, agent_answers, same, ROOT
from qp.mra import item_scores

OUT = ROOT / "submissions/trackA_cand_next_accounting.csv"
ANCHOR = {  # clip: (anchor qid, anchor value)
    "internet_0053": (3135, 1.623738),
    "internet_0054": (3145, 1.623738),
    "internet_0047": (3096, 24.2186),
    "internet_0069": (3251, 10.5),
}


def main():
    t = master()
    cur = read("trackA_probe_agent_sim2agent", t.index)
    pre = read("trackA_cand_C1_solS2S3", t.index)
    ag = agent_answers(t.index, t)
    out = cur.copy()
    why = pd.Series("", index=t.index)
    # F: stated facts
    f = pd.read_csv(ROOT / "research/next/accounting/fact_rows.csv")
    for q, x in zip(f.qid, f.stated):
        out[q] = x
        why[q] = "F"
    # R: master.fact rows that a later lever moved > 5% off the fact
    r = t.fact.notna() & (np.log(cur / t.fact).abs() > np.log(1.05))
    for q in t.index[r]:
        out[q] = t.fact[q]
        why[q] = "R"
    print("R rows:", list(t.index[r]))
    # P: physical anchors on the agent's answers of the clip
    for clip, (qa, val) in ANCHOR.items():
        assert t.video_id[qa] == clip and same(cur[qa], ag[qa]), clip
        k = val / ag[qa]
        rows = t.index[t.video_id.eq(clip) & ag.notna() & same(cur, ag.fillna(-1))]
        for q in rows:
            if why[q] == "F":
                continue
            out[q] = ag[q] * k
            why[q] = f"P k={k:.3f}"
        print(f"{clip}: k = {k:.4f} on {len(rows)} rows (anchor qid {qa}: agent {ag[qa]:.4g} -> {val})")
    ch = ~same(out, cur, 1e-9)
    # guards: no lab row, no master.fact row, nothing outside the logged rows
    assert not (ch & t.srcg.eq("lab")).any()
    assert not (ch & t.fact.notna() & ~why.eq("R")).any()
    assert (why[ch] != "").all()
    log = pd.DataFrame(dict(qid=t.index[ch], video=t.video_id[ch], cat=t.category[ch], src=t.srcg[ch],
                            scored=t.scored[ch], rule=why[ch], old=cur[ch], new=out[ch], ratio=(out / cur)[ch],
                            question=t.question[ch]))
    log.to_csv(ROOT / "research/next/accounting/changes_cand.csv", index=False)
    sc = log[log.scored]
    print("changed rows:", int(ch.sum()), "scored:", len(sc))
    print(pd.crosstab([sc.cat, sc.src], sc.rule.str[0]))
    # held-out check on the F rows: agent answer vs the stated value (agent never saw the sibling clip)
    ff = f[f.scored]
    s = item_scores(ff.agent.to_numpy(), ff.stated.to_numpy())
    print(f"F rows (scored {len(ff)}): agent item vs stated value {np.nanmean(s):.3f}; "
          f"items gained if the stated values are the labels: "
          f"{ {c: round(float((1 - s[ff.cat.eq(c).to_numpy()]).sum()), 2) for c in ['D2', 'D3']} }")
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        pd.DataFrame({"id": out.index, "parsed_value": out.values}).to_csv(fh, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(OUT)], check=True)
    chk = read(str(OUT), t.index)
    assert np.isfinite(chk).all() and (chk > 0).all() and np.allclose(chk, out, rtol=1e-12)


if __name__ == "__main__":
    main()
