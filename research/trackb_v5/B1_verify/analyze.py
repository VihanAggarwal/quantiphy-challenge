"""Verifier analysis of B1 on the independent re-derivation (indep_b1.py): row counts per category, attribution,
spill-over, B1_rows.csv / B1_spillover.csv consistency, lab rows vs v5, stated facts, validation-overlap rows."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.argv = ["x"]
sys.path.insert(0, str(Path(__file__).parent))
import indep_b1 as I  # noqa: E402

ROOT = I.ROOT
T, tq, qids = I.T, I.tq, I.qids
scored = pd.Series(~I.D.dup, index=qids)
CATS = ("S2", "D2", "S3", "D3")
B1 = pd.read_csv(ROOT / "submissions/trackB_cand_B1.csv").set_index("id").parsed_value.reindex(qids)
V3 = pd.read_csv(ROOT / "submissions/trackB_v3_catmedian_famrules.csv").set_index("id").parsed_value.reindex(qids)
V5 = pd.read_csv(ROOT / "submissions/trackB_cand_v5.csv").set_index("id").parsed_value.reindex(qids)


def ch(a, b):
    return pd.Series(I.diff(a, b), index=a.index)


def pc(mask):
    return {c: f"{int((mask & (tq.category == c)).sum())}/{int((mask & scored & (tq.category == c)).sum())}" for c in CATS}


ALL = dict(l2q=True, s2route=True, l6s=True, l1=True, l4=True, clamp=True)
raw0, post0, f0, st0, _ = I.build()
rawB, postB, fB, stB, infoB = I.build(**ALL)
assert not ch(fB, B1).any()
chg = ch(B1, V3)
print("B1 vs v3 changed (all/scored):", pc(chg), "total", int(chg.sum()), int((chg & scored).sum()))
print("raw changed vs base raw:", pc(ch(rawB, raw0)))

TARGET = {"l2q": ("S3", "D3"), "s2route": ("S2",), "l6s": ("D2",), "l1": ("S3",), "l4": ("D2",), "clamp": CATS}
att = {q: [] for q in qids}
spill_rows = {}
for k in ALL:
    r1, p1, f1, _, _ = I.build(**{k: True})
    a1 = ch(f1, V3)
    sp = a1 & ~ch(r1, raw0)
    sp_out = sp & ~tq.category.isin(TARGET[k])
    sp_in = sp & tq.category.isin(TARGET[k])
    lo = dict(ALL)
    lo[k] = False
    fl = I.build(**lo)[2]
    loo = ch(B1, fl)
    for q in loo.index[loo]:
        att[q].append(k)
    if k in ("s2route", "l6s", "l2q"):
        spill_rows[k] = sp
    print(f"{k:8s} alone {pc(a1)} | spill out-of-target {pc(sp_out)} (n={int(sp_out.sum())}) in-target pool-only {pc(sp_in)}"
          f" | LOO {pc(loo)}")
una = [q for q in qids if chg[q] and not att[q]]
print("changed rows with no LOO attribution:", len(una))

# B1_rows.csv consistency
R = pd.read_csv(ROOT / "research/trackb_v5/B1_rows.csv", index_col=0)
Rc = R[R.changed]
print("B1_rows.csv rows", len(R), "changed rows", len(Rc), "== my changed set:", set(Rc.index) == set(chg.index[chg]))
mine = pd.Series({q: "+".join(v) for q, v in att.items()})
print("B1_rows.csv attribution identical:", (Rc.components.fillna("") == mine.reindex(Rc.index).fillna("")).all())
print("B1_rows.csv values: b1 col == B1 file:", np.allclose(Rc.b1, B1.reindex(Rc.index)),
      "v3 col == v3 file:", np.allclose(Rc.v3, V3.reindex(Rc.index)))
SP = pd.read_csv(ROOT / "research/trackb_v5/B1_spillover.csv")
print("B1_spillover.csv columns", SP.columns.tolist(), "rows", len(SP))
myspill = set()
for k, m in spill_rows.items():
    out = m & ~tq.category.isin(TARGET[k])
    myspill |= set(m.index[out])
idcol = [c for c in SP.columns if c in ("qid", "id", "Unnamed: 0")][0]
print("spill-over rows (out-of-target) mine", len(myspill), "| file", SP[idcol].nunique(),
      "| file ⊇ mine", myspill <= set(SP[idcol]), "| all spill rows changed in B1", all(chg[q] for q in set(SP[idcol])))
allspill = set().union(*[set(m.index[m]) for m in spill_rows.values()])
print("spill rows incl. in-target pool-only:", len(allspill), "== file set:", allspill == set(SP[idcol]))

# lab rows of S3/D3 vs v5
lab = (tq.video_source == "lab") & tq.category.isin(["S3", "D3"])
print("S3/D3 lab rows", int(lab.sum()), "differing from v5:", int((ch(B1, V5) & lab).sum()))
nl = ~lab & tq.category.isin(["S3", "D3"]) & ch(B1, V5)
print("non-lab S3/D3 rows differing from v5:", tq.category[nl].value_counts().to_dict())

# stated-fact rows: final unchanged
st = set(stB) | set(st0)
print("stated rows (rule-set) base", len(st0), "B1", len(stB), "same set", st0 == stB,
      "changed vs v3:", int(chg[list(st)].sum()))
fl = pd.read_csv(ROOT / "research/trackb_dense/out/fact_labels.csv", index_col=0)
fl = fl[fl.index < 100000]
print("fact_labels rows", len(fl), "changed vs v3:", int(chg.reindex(fl.index).sum()))

# validation-overlap rows
dup = ~scored
print("validation-overlap test rows", int(dup.sum()), "changed in B1:", pc(chg & dup))
val = I.D.val
key = dict(zip(zip(val.video_id, val.question.map(I.pp.norm_question)), val.answer))
lab_of = pd.Series({q: key.get((tq.video_id[q], I.pp.norm_question(tq.question[q])), np.nan) for q in qids[dup.to_numpy()]})
m = chg[lab_of.index]
eqv = np.isclose(B1[lab_of.index][m], lab_of[m], rtol=1e-6)
eqv3 = np.isclose(V3[lab_of.index][m], lab_of[m], rtol=1e-6)
print(f"  changed overlap rows {int(m.sum())}: B1 == validation label on {int(eqv.sum())} (v3 == label on {int(eqv3.sum())})")
if eqv.any():
    qq = lab_of[m].index[eqv]
    for q in qq:
        mem = [k for k, v in I.M.items() if np.isfinite(v[np.where(qids == q)[0][0]]) and np.isclose(v[np.where(qids == q)[0][0]], B1[q], rtol=1e-9)]
        print("   ", q, tq.video_id[q], B1[q], "label", lab_of[q], "open member equal:", mem, "clamp:", q in infoB["clamp"])
pd.DataFrame({"changed": chg, "components": mine, "category": tq.category, "scored": scored}).to_csv(
    Path(__file__).parent / "my_rows.csv")
