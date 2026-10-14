"""Master per-row table for the gate study (test inputs + cached Claude runs only; no labels).
Writes research/gates/out/base.csv"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from qp.data import load_test
OUT = ROOT / "research/gates/out"; OUT.mkdir(parents=True, exist_ok=True)
t = load_test().set_index("qid")
q = t.question.str.lower()
t["kind"] = np.where(q.str.contains("acceler|veloc|speed|travel"), "motion", "static")
t["src"] = t.video_source.replace({"segmentation": "simulation"})
t["dim3"] = t.category.str[1] == "3"
t["sub"] = np.where(~t.dim3, "2D", np.where(t.src == "lab", "lab", "3Dnl"))
def rd(p):
    d = pd.read_csv(ROOT / p); d = d.rename(columns={d.columns[0]: "id"}).set_index("id"); return d
def sub_(p):
    return rd(p).parsed_value.astype(float).reindex(t.index)
R = {"a": rd("runs/test_v1_high_854/test.csv"), "b": rd("runs/test_3dnl_v1_high_b/test.csv"),
     "c": rd("runs/test_3dnl_v2_high/test.csv")}
for k, d in R.items():
    d = d.reindex(t.index)
    for c in ("parsed_value", "geo_value", "direct_value"):
        t[f"{c[:3]}_{k}"] = pd.to_numeric(d[c], errors="coerce")
    t[f"meth_{k}"] = d["method"]; t[f"flags_{k}"] = d["flags"]; t[f"gmeth_{k}"] = d["geo_method"]
def lmed(cols):
    L = np.log(t[cols].where(t[cols] > 0)); return np.exp(L.median(axis=1, skipna=True))
t["dmed"] = lmed(["dir_a", "dir_b", "dir_c"]); t["gmed"] = lmed(["geo_a", "geo_b", "geo_c"])
t["combo3"] = sub_("submissions/trackA_combo3_on_combo2.csv")
t["combo2"] = sub_("submissions/trackA_cand_combo2.csv")
t["physb2"] = sub_("submissions/trackA_cand_physb2_on_p21.csv")
t.drop(columns=["video_path", "depth_info"]).to_csv(OUT / "base.csv")
close = lambda a, b: np.isclose(a, b, rtol=1e-6)
t["eq_par"] = close(t.combo3, t.par_a); t["eq_geo"] = close(t.combo3, t.geo_a); t["eq_dir"] = close(t.combo3, t.dir_a)
t["eq_dmed"] = close(t.combo3, t.dmed); t["eq_gm"] = close(t.combo3, np.sqrt(t.geo_a * t.dir_a))
g = t.groupby(["category", "sub", "src", "kind"])
print(g[["eq_par", "eq_geo", "eq_dir", "eq_dmed", "eq_gm"]].mean().round(2).assign(n=g.size()).to_string())
