"""Review checks for research/internet/ (validation labels for EVALUATION only):
1. structure of every internet candidate CSV vs probe 8; 2. scored (non-overlap) changed rows;
3. TWIN premise on the twins whose original is a validation question; 4. PHYSB size under both label hypotheses."""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp.data import load_split  # noqa: E402
from qp.mra import item_scores  # noqa: E402

df = load_split("test").set_index("qid")
val = pd.read_csv(ROOT / "data/QuantiPhy-validation/validation_dataset.csv")
ov = set(zip(val.video_id, val.question.str.strip()))
df["overlap"] = [(v, q.strip()) in ov for v, q in zip(df.video_id, df.question)]
B = pd.read_csv(ROOT / "submissions/trackA_probe8_p7b_d2fixes_d3labphys.csv")
base = B.set_index("id").parsed_value
for n in ["fwd", "winacc", "fam", "main", "physb", "verified"]:
    c = pd.read_csv(ROOT / f"submissions/trackA_cand_internet_{n}_on_p8.csv")
    same = (len(c) == 3289 and (c.id.values == B.id.values).all()
            and (c.drop(columns="parsed_value").fillna("").astype(str).values
                 == B.drop(columns="parsed_value").fillna("").astype(str).values).all())
    v = c.parsed_value.to_numpy(float)
    d = ~np.isclose(v, base.values, rtol=1e-9)
    ids = c.id[d]
    sc = [i for i in ids if not df.overlap[i]]
    print(f"{n:9s} template-identical {same} finite>0 {np.isfinite(v).all() and (v > 0).all()} changed {d.sum()} "
          f"{df.category[ids].value_counts().to_dict()} scored {len(sc)} {df.category[sc].value_counts().to_dict()} "
          f"non-internet {sorted({x for x in c.video_id[d] if not x.startswith('internet')})}")

nq = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())  # noqa: E731
lab = {(a, nq(q)): g for a, q, g in zip(val.video_id, val.question, val.ground_truth_posterior)}
fam = pd.read_csv(ROOT / "submissions/trackA_cand_internet_fam_on_p8.csv").set_index("id").parsed_value
pairs = [(2949, 2018), (2952, 2021), (2971, 2092), (2972, 2093), (2973, 2094), (2974, 2095), (2975, 2096),
         (2976, 2097), (2977, 2098)]
s0 = s1 = l0 = l1 = k = 0
for t, o in pairs:
    g = lab.get((df.video_id[o], nq(df.question[o])))
    if g is None:
        continue
    k += 1
    s0 += item_scores([base[t]], [g])[0]; s1 += item_scores([fam[t]], [g])[0]
    l0 += abs(np.log(base[t] / g)); l1 += abs(np.log(fam[t] / g))
print(f"TWIN premise (n={k}): item sum {s0:.1f} -> {s1:.1f}; mean |log err| {l0 / k:.4f} -> {l1 / k:.4f}")

c = pd.read_csv(ROOT / "submissions/trackA_cand_internet_physb_on_p8.csv").set_index("id").parsed_value
ids = c.index[~np.isclose(c, base, rtol=1e-9)]
a = (item_scores(c[ids], base[ids]).sum() - item_scores(base[ids], base[ids]).sum()) / 1137
p = (item_scores(c[ids], c[ids]).sum() - item_scores(base[ids], c[ids]).sum()) / 1137
print(f"PHYSB n={len(ids)}: D2 {a:+.4f} if labels in-clip, {p:+.4f} if physical (overall /4)")
