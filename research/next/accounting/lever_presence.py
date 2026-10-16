"""Part (1): is every earlier lever still in the current best (trackA_probe_agent_sim2agent.csv)?

For each lever = (candidate file, the file it was built on, categories), take the rows it changed and classify the
current best's value on each row:
  kept     current == lever value
  agent    current == agent answer (the agent replaced the row; lever value lost by design of build_agent_sub.py)
  reverted current == the lever's base value (lever lost)
  other    something else (a later lever changed the row again)
Counts are over scored rows (master.scored) and split lab / non-lab.  LB = leaderboard read of that lever (PROBES.md).

    .venv/bin/python research/next/accounting/lever_presence.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from load import master, read, agent_answers, same

# (name, candidate, base, categories, leaderboard read per category from PROBES.md)
LEVERS = [
    ("p5 families (vs v3)", "trackA_probe5_families_merged", "trackA_v3_best_per_category", "S2,D2,S3,D3", "+.010/+.025/+.028/+.043"),
    ("p7a 3D-nonlab ensemble", "trackA_probe7a_p5_ensemble3dnl", "trackA_probe5_families_merged", "S3,D3", "unread"),
    ("p7b family ext", "trackA_probe7b_p5_ens_famext", "trackA_probe7a_p5_ensemble3dnl", "D2,S3,D3", "unread"),
    ("p8 D2 0191/shark", "trackA_probe8_p7b_d2fixes_d3labphys", "trackA_probe7b_p5_ens_famext", "D2", "unread (8 vs 7b)"),
    ("p8 D3 lab clock+fits", "trackA_probe8_p7b_d2fixes_d3labphys", "trackA_probe7b_p5_ens_famext", "D3", "unread"),
    ("p11 S3 labnoise sz2", "trackA_probe11_p8_emu_labnoise", "trackA_probe8_p7b_d2fixes_d3labphys", "S3", "S3 +.015"),
    ("p11 D3 labnoise emu", "trackA_probe11_p8_emu_labnoise", "trackA_probe8_p7b_d2fixes_d3labphys", "D3", "D3 +.001"),
    ("p18 S2 sizeenv", "trackA_probe18_p16_physb_sizeenv_sim3d", "trackA_best_p16_p8_labnoiseS3D3", "S2", "S2 +.002"),
    ("p18 D2 PHYSB", "trackA_probe18_p16_physb_sizeenv_sim3d", "trackA_best_p16_p8_labnoiseS3D3", "D2", "D2 +.009"),
    ("p18 S3 sim3d motionfam", "trackA_probe18_p16_physb_sizeenv_sim3d", "trackA_best_p16_p8_labnoiseS3D3", "S3", "S3 +.003"),
    ("p18 D3 sim3d motionfam", "trackA_probe18_p16_physb_sizeenv_sim3d", "trackA_best_p16_p8_labnoiseS3D3", "D3", "D3 +.001"),
    ("p17 S3 labsize", "trackA_probe17_p16_stack", "trackA_best_p16_p8_labnoiseS3D3", "S3", "S3 +.001"),
    ("p17 D3 labsize+labdist", "trackA_probe17_p16_stack", "trackA_best_p16_p8_labnoiseS3D3", "D3", "D3 +.005"),
    ("p17 S2 internet_verified", "trackA_probe17_p16_stack", "trackA_best_p16_p8_labnoiseS3D3", "S2", "S2 0 (not merged)"),
    ("p17 D2 inet+d2static", "trackA_probe17_p16_stack", "trackA_best_p16_p8_labnoiseS3D3", "D2", "D2 -.001 (not merged)"),
    ("physb2 D2", "trackA_cand_physb2_on_p21", "trackA_best_p21", "D2", "D2 +.006"),
    ("path85 combo (all)", "trackA_cand_path85_combo", "trackA_cand_physb2_on_p21", "S2,D2,S3,D3", "in combo2"),
    ("combo2 S2", "trackA_cand_combo2", "trackA_cand_physb2_on_p21", "S2", "S2 +.010"),
    ("combo2 D2", "trackA_cand_combo2", "trackA_cand_physb2_on_p21", "D2", "D2 +.004"),
    ("combo2 S3", "trackA_cand_combo2", "trackA_cand_physb2_on_p21", "S3", "S3 +.001"),
    ("combo2 D3", "trackA_cand_combo2", "trackA_cand_physb2_on_p21", "D3", "D3 +.008"),
    ("combo3 S2 (simmot gm + inet direct)", "trackA_combo3_on_combo2", "trackA_cand_combo2", "S2", "S2 +.004"),
    ("combo3 S3 (no mid-ball)", "trackA_combo3_on_combo2", "trackA_cand_combo2", "S3", "S3 +.003"),
    ("combo3 D3 (emu4 + labstat gm)", "trackA_combo3_on_combo2", "trackA_cand_combo2", "D3", "D3 +.002"),
    ("C1 S2 (const-acc pool)", "trackA_cand_C1_on_combo3", "trackA_combo3_on_combo2", "S2", "S2 0"),
    ("C1 D2 (facts + 0020)", "trackA_cand_C1_on_combo3", "trackA_combo3_on_combo2", "D2", "D2 +.005"),
    ("C1 S3", "trackA_cand_C1_on_combo3", "trackA_combo3_on_combo2", "S3", "S3 +.003"),
    ("C1 D3", "trackA_cand_C1_on_combo3", "trackA_combo3_on_combo2", "D3", "D3 +.001"),
    ("Sol S2", "trackA_cand_C1_solS2S3", "trackA_cand_C1_on_combo3", "S2", "S2 +.003"),
    ("Sol S3", "trackA_cand_C1_solS2S3", "trackA_cand_C1_on_combo3", "S3", "S3 +.003"),
    # built but never merged / negative or unread
    ("U1 S3 sz4", "trackA_u1_p22s2d2_s3sz4_d3emu3", "trackA_cand_physb2_on_p21", "S3", "S3 -.011 (rejected)"),
    ("U1 D3 emu3", "trackA_u1_p22s2d2_s3sz4_d3emu3", "trackA_cand_physb2_on_p21", "D3", "D3 +.001 (emu4 used)"),
    ("U3 D3 labstat direct", "trackA_u3_s3nomid_d3labdirect", "trackA_cand_physb2_on_p21", "D3", "D3 -.002 (rejected)"),
    ("U4 S3 labstat direct", "trackA_u4_s3labdirect_d3labgm", "trackA_cand_physb2_on_p21", "S3", "S3 -.004 (rejected)"),
    ("U2 S3 no path", "trackA_u2_p23s2d2_s3nopath_d3emu4", "trackA_cand_physb2_on_p21", "S3", "S3 -.004 (rejected)"),
]


def main():
    t = master()
    cur = read("trackA_probe_agent_sim2agent", t.index)
    ag = agent_answers(t.index, t)
    cache = {}
    rows = []
    for name, cand, base, cats, lb in LEVERS:
        c = cache.setdefault(cand, read(cand, t.index))
        b = cache.setdefault(base, read(base, t.index))
        m = ~same(c, b, 1e-9) & t.category.isin(cats.split(",")) & t.scored
        for grp, gm in (("lab", t.srcg.eq("lab")), ("nonlab", t.srcg.ne("lab"))):
            mm = m & gm
            if not mm.any():
                continue
            kept = mm & same(cur, c)
            agent = mm & ~kept & ag.notna() & same(cur, ag.fillna(-1))
            rev = mm & ~kept & ~agent & same(cur, b)
            oth = mm & ~kept & ~agent & ~rev
            rows.append(dict(lever=name, grp=grp, n=int(mm.sum()), kept=int(kept.sum()), agent=int(agent.sum()),
                             reverted=int(rev.sum()), other=int(oth.sum()), lb=lb,
                             cats=t.category[mm].value_counts().to_dict()))
    out = pd.DataFrame(rows)
    pd.set_option("display.width", 250, "display.max_colwidth", 60)
    print(out.to_string(index=False))
    out.to_csv(__file__.replace("lever_presence.py", "lever_presence.csv"), index=False)


if __name__ == "__main__":
    main()
