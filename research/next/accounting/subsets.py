"""Part (3): per-subset item means of the current best (sim2agent) on the NEW scored set, and the loss each holds.
Inputs (all from PROBES.md / loss_audit.md, no labels): combo3-era subset means (loss_audit section 2, diagE/F decode),
C1 / Sol / combo3 reads, the three same-day agent reads, and the H1 removed-row proxy means (scored_set.py).
Lab rows are identical to combo3 in every file since combo3, so lab subset means carry over; non-lab means follow
from the category totals.  Precision: about +-.01 per subset (3-decimal rounding x N / n, proxy noise).
    .venv/bin/python research/next/accounting/subsets.py"""
import pandas as pd
R = pd.read_csv(__file__.replace("subsets.py", "scored_set.csv"))
def prox(f, c, col="mean_removed_proxy"):
    return float(R[(R.file == f) & (R.cat == c)][col].iloc[0])
N_new = dict(S2=532, D2=1109, S3=488, D3=881)
cur = dict(S2=.863, D2=.875, S3=.813, D3=.832)
rows = []
# S3 / D3: lab means from combo3 (loss audit) minus removed lab rows (proxy, C1 = combo3 on lab)
s3lab_old, n_s3lab_old = .789, 317
s3lab = (s3lab_old * n_s3lab_old - prox("A:cand_C1_on_combo3", "S3", "lab") * 35) / (n_s3lab_old - 35)
d3lab_old = (.802 * 334 + .76 * 105) / 439
d3lab = (d3lab_old * 439 - prox("A:cand_C1_on_combo3", "D3", "lab") * 36) / (439 - 36)
s3sim = (cur["S3"] * 488 - s3lab * 282) / 206
d3sim = (cur["D3"] * 881 - d3lab * 403) / 478
# S2: base (C1_solS2S3) sim .851 / internet .802 on the old set (combo3 audit split, scaled to the measured .834)
s2sim_base = (.851 * 362 - prox("A:cand_C1_on_combo3", "S2") * 21) / 341
s2inet_agent = (.852 * 532 - s2sim_base * 341) / 191          # sim2base: base sim2 + agent internet
s2sim_agent = (cur["S2"] * 532 - s2inet_agent * 191) / 341
# D2: base sim (static .861 incl. C1, motion .88), internet .88 (bucket est.), lab ~.80 (15 rows)
d2sim_base = ((.861 * 719 + .88 * 202) - prox("A:cand_C1_on_combo3", "D2") * 27) / 894
d2lab = .80
d2inet_base = .88
d2inet_agent = (.853 * 1109 - d2sim_base * 894 - d2lab * 15) / 200   # sim2base: base sim + agent internet
d2sim_agent = (cur["D2"] * 1109 - d2inet_agent * 200 - d2lab * 15) / 894
T = [("S2", "sim (2D)", 341, s2sim_agent, s2sim_base), ("S2", "internet", 191, s2inet_agent, .802),
     ("D2", "sim (2D)", 894, d2sim_agent, d2sim_base), ("D2", "internet", 200, d2inet_agent, d2inet_base),
     ("D2", "lab", 15, d2lab, d2lab), ("S3", "lab", 282, s3lab, s3lab), ("S3", "sim (3D)", 206, s3sim, None),
     ("D3", "lab", 403, d3lab, d3lab), ("D3", "sim (3D)", 478, d3sim, None)]
for cat, sub, n, m, mb in T:
    rows.append(dict(cat=cat, subset=sub, n_new=n, mean_now=m, mean_pre_agent=mb, loss_overall=(1 - m) * n / N_new[cat] / 4))
d = pd.DataFrame(rows).sort_values("loss_overall", ascending=False)
print(d.round(4).to_string(index=False)); print("total loss", round(d.loss_overall.sum(), 4), "-> overall", round(1 - d.loss_overall.sum(), 4))
