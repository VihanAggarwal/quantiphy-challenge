"""Loss audit master table (analysis only; validation labels and stated facts used ONLY to measure errors).
Writes research/r86/loss_audit/master.pkl. No API, no repo code modified."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from qp.mra import item_scores  # noqa
OUT = Path(__file__).parent
S = ROOT / "submissions"

def read_sub(p):
    d = pd.read_csv(p); d = d.rename(columns={d.columns[0]: "id"}).set_index("id")["parsed_value"].astype(float); return d

t = pd.read_pickle(ROOT / "research/path85_strategy/out/table.pkl")
for nm, f in (("physb2", "trackA_cand_physb2_on_p21.csv"), ("combo2", "trackA_cand_combo2.csv"),
              ("combo3", "trackA_combo3_on_combo2.csv")):
    t[nm] = read_sub(S / f).reindex(t.index)
t["scored"] = ~t.overlap
# 3-run direct median (3D non-lab members)
with np.errstate(all="ignore"):
    L = np.log(t[["d1", "d2", "d3"]].where(t[["d1", "d2", "d3"]] > 0))
t["dmed"] = np.exp(L.median(axis=1, skipna=True))
# stated facts (exact test labels from family statements), from the raw-run facts log
f = pd.read_csv(ROOT / "research/path85_strategy/out/facts_log.csv")
f = f[f.applied].drop_duplicates("qid", keep="first").set_index("qid")
t["fact"] = f.new.reindex(t.index)
t["fact_rule"] = f.rule.reindex(t.index)
# subset as the leaderboard decoding partitions it
def subset(r):
    c, s, m = r.category, r.srcg, r.motion
    if c == "S2": return "S2:sim+seg" if s == "sim" else "S2:internet"
    if c == "D2": return "D2:sim-static" if (s == "sim" and not m) else "D2:rest"
    if c == "S3": return "S3:sim+seg" if s == "sim" else "S3:lab"
    if c == "D3": return "D3:lab-static" if (s == "lab" and not m) else "D3:rest"
t["subset"] = t.apply(subset, axis=1)
t["kg"] = t.kind.map({"size": "size", "dist": "distance", "path": "distance", "speed": "speed",
                      "avgspeed": "speed", "acc": "accel"})
# provenance of the final (combo3) answer
def prov(r):
    v = r.combo3
    if pd.notna(r.fact) and np.isclose(v, r.fact, rtol=1e-6): return "fact"
    if np.isclose(v, r.r_parsed_value, rtol=1e-6):
        return "raw:" + ("geo" if str(r.r_method).startswith("geometry") else "direct")
    if pd.notna(r.dmed) and np.isclose(v, r.dmed, rtol=1e-6): return "dmed"
    if np.isclose(v, r.physb2, rtol=1e-6): return "rule<=physb2"
    return "rule>physb2"
t["prov"] = t.apply(prov, axis=1)
t["sc_val"] = item_scores(t.combo3, t.val)
t["lr_val"] = np.log(t.combo3 / t.val)
t["sc_fact_raw"] = item_scores(t.r_parsed_value.where(~((t.category.isin(["S3", "D3"])) & (t.srcg == "sim")), t.dmed), t.fact)
t["lr_fact_raw"] = np.log(t.r_parsed_value.where(~((t.category.isin(["S3", "D3"])) & (t.srcg == "sim")), t.dmed) / t.fact)
t.to_pickle(OUT / "master.pkl")
print(t.groupby(["subset", "kg"]).agg(n=("scored", "size"), scored=("scored", "sum"), val=("val", "count"),
                                     fact=("fact", "count")).to_string())
print(t.prov.value_counts())
print(pd.crosstab(t.subset, t.prov))
