"""Lab rows: attribute the current best's value to the last file in the best-of chain that changed it, and check that
lab rows of the current best equal the pre-agent base and combo3 (no lab lever lost after combo3).
    .venv/bin/python research/next/accounting/lab_chain.py"""
import numpy as np, pandas as pd
from load import master, read, same
CHAIN = ["trackA_v3_best_per_category", "trackA_probe5_families_merged", "trackA_probe7a_p5_ensemble3dnl",
         "trackA_probe7b_p5_ens_famext", "trackA_probe8_p7b_d2fixes_d3labphys", "trackA_best_p16_p8_labnoiseS3D3",
         "trackA_best_p21", "trackA_cand_physb2_on_p21", "trackA_cand_path85_combo", "trackA_cand_combo2",
         "trackA_combo3_on_combo2", "trackA_cand_C1_on_combo3", "trackA_cand_C1_solS2S3", "trackA_probe_agent_sim2agent"]
t = master(); V = {c: read(c, t.index) for c in CHAIN}
lab = t.srcg.eq("lab") & t.scored
cur = V[CHAIN[-1]]
for c in CHAIN[-4:-1]:
    print(f"lab scored rows differing from {c}: {int((lab & ~same(cur, V[c], 1e-9)).sum())}")
last = pd.Series("v3", index=t.index)
for a, b in zip(CHAIN[:-1], CHAIN[1:]):
    ch = ~same(V[a], V[b], 1e-9)
    last[ch] = b.replace("trackA_", "")
print(pd.crosstab(last[lab], t.category[lab]))
