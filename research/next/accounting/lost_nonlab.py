"""Non-lab levers the agent overwrote: does the agent already carry the lever's information?

For each lever's changed rows (now holding the agent answer), compare
  r_lev = ln(lever value / pre-lever value)    what the lever did
  r_ag  = ln(agent / pre-lever value)          where the agent sits relative to the pre-lever answer
If r_ag ~ 0 while r_lev is large, the agent repeated the error the lever fixed (lever lost).
If r_ag ~ r_lev, the agent found the same answer itself (nothing lost).
Reported per lever (scored rows): median r_lev, median r_ag, share of rows where the agent is closer to the pre-lever
value than to the lever value ("agent ~ pre").

    .venv/bin/python research/next/accounting/lost_nonlab.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from load import master, read, agent_answers, same

LEVERS = [
    ("p18 D2 PHYSB", "trackA_probe18_p16_physb_sizeenv_sim3d", "trackA_best_p16_p8_labnoiseS3D3", "D2"),
    ("physb2 D2", "trackA_cand_physb2_on_p21", "trackA_best_p21", "D2"),
    ("p18 S2 sizeenv", "trackA_probe18_p16_physb_sizeenv_sim3d", "trackA_best_p16_p8_labnoiseS3D3", "S2"),
    ("p18 S3 sim3d motionfam", "trackA_probe18_p16_physb_sizeenv_sim3d", "trackA_best_p16_p8_labnoiseS3D3", "S3"),
    ("p18 D3 sim3d motionfam", "trackA_probe18_p16_physb_sizeenv_sim3d", "trackA_best_p16_p8_labnoiseS3D3", "D3"),
    ("p8 D2 0191/shark", "trackA_probe8_p7b_d2fixes_d3labphys", "trackA_probe7b_p5_ens_famext", "D2"),
    ("path85 combo S2", "trackA_cand_path85_combo", "trackA_cand_physb2_on_p21", "S2"),
    ("path85 combo D2", "trackA_cand_path85_combo", "trackA_cand_physb2_on_p21", "D2"),
    ("path85 combo D3", "trackA_cand_path85_combo", "trackA_cand_physb2_on_p21", "D3"),
    ("combo2-combo D2 (ffbd,E2,L1)", "trackA_cand_combo2", "trackA_cand_path85_combo", "D2"),
    ("combo2-combo D3 (ffbd)", "trackA_cand_combo2", "trackA_cand_path85_combo", "D3"),
    ("combo3 S2", "trackA_combo3_on_combo2", "trackA_cand_combo2", "S2"),
    ("C1 S2", "trackA_cand_C1_on_combo3", "trackA_combo3_on_combo2", "S2"),
    ("C1 D2", "trackA_cand_C1_on_combo3", "trackA_combo3_on_combo2", "D2"),
    ("C1 D3", "trackA_cand_C1_on_combo3", "trackA_combo3_on_combo2", "D3"),
    ("p7b fam ext D2", "trackA_probe7b_p5_ens_famext", "trackA_probe7a_p5_ensemble3dnl", "D2"),
    ("p7b fam ext D3", "trackA_probe7b_p5_ens_famext", "trackA_probe7a_p5_ensemble3dnl", "D3"),
    ("p7b fam ext S3", "trackA_probe7b_p5_ens_famext", "trackA_probe7a_p5_ensemble3dnl", "S3"),
    ("p5 fam D3 nonlab", "trackA_probe5_families_merged", "trackA_v3_best_per_category", "D3"),
    ("p5 fam D2", "trackA_probe5_families_merged", "trackA_v3_best_per_category", "D2"),
]


def main(verbose=("p18 D2 PHYSB", "physb2 D2", "C1 D2", "C1 D3", "p8 D2 0191/shark", "p18 S3 sim3d motionfam",
                  "p18 D3 sim3d motionfam", "combo2-combo D2 (ffbd,E2,L1)", "combo2-combo D3 (ffbd)")):
    t = master()
    cur = read("trackA_probe_agent_sim2agent", t.index)
    ag = agent_answers(t.index, t)
    rows, detail = [], []
    for name, cand, base, cats in LEVERS:
        c, b = read(cand, t.index), read(base, t.index)
        m = ~same(c, b, 1e-9) & t.category.isin(cats.split(",")) & t.scored & t.srcg.ne("lab") & ag.notna() & same(cur, ag.fillna(-1))
        if not m.any():
            continue
        rl = np.log(c[m] / b[m]); ra = np.log(ag[m] / b[m])
        closer_pre = (ra.abs() < (ra - rl).abs())
        rows.append(dict(lever=name, n=int(m.sum()), med_r_lev=rl.median(), med_abs_r_lev=rl.abs().median(),
                         med_r_ag=ra.median(), med_abs_ag_minus_lev=(ra - rl).abs().median(),
                         share_agent_closer_to_pre=closer_pre.mean()))
        if name in verbose:
            dd = pd.DataFrame(dict(lever=name, video=t.video_id[m], cat=t.category[m], q=t.question[m].str[:70],
                                   prior=t.prior[m].str[:40], pre=b[m], lever_val=c[m], agent=ag[m], fact=t.fact[m]))
            detail.append(dd)
    pd.set_option("display.width", 250, "display.max_colwidth", 70, "display.max_rows", 500)
    print(pd.DataFrame(rows).round(3).to_string(index=False))
    if detail:
        D = pd.concat(detail)
        D.to_csv(__file__.replace("lost_nonlab.py", "lost_nonlab_detail.csv"))
        print(D.round(4).to_string())


if __name__ == "__main__":
    main()
