"""Track B loss map (analysis only): Track B v3 answers vs (a) validation labels (overlap rows) and (b) the Track A
combo3 answers as a proxy reference (A is ~.82 MRA; agreement with A is NOT a label). Item score of B scored against A
('pseudo-MRA') ranks where B's errors concentrate; per-row weights as on the leaderboard."""
import numpy as np, pandas as pd
from pathlib import Path
import sys
OUT = Path(__file__).parent
sys.path.insert(0, str(OUT.parents[2]))
from qp.mra import item_scores
t = pd.read_pickle(OUT / "master.pkl")
d = pd.read_csv(OUT.parents[2] / "submissions/trackB_v3_catmedian_famrules.csv")
t["B"] = d.rename(columns={d.columns[0]: "id"}).set_index("id").parsed_value.reindex(t.index).astype(float)
NC = {"S2": 553, "D2": 1137, "S3": 538, "D3": 933}
def bucket(r):
    c, src, kg = r.category, r.srcg, r.kg
    if c in ("S2", "S3"): return f"{c} {src} {kg}"
    if c == "D2": return f"D2 {src} {kg}"
    return f"D3 {src} {kg}"
s = t[t.scored].copy()
s["bk"] = s.apply(bucket, axis=1)
s["vsA"] = item_scores(s.B, s.combo3)
s["w"] = s.category.map(lambda c: 1 / (4 * NC[c]))
g = s.groupby("bk")
m = pd.DataFrame({"n": g.size(), "B_vs_A": g.vsA.mean(), "gross>1.5x": g.apply(lambda x: (np.abs(np.log(x.B / x.combo3)) > np.log(1.5)).mean()),
                  "pts_if_B=A_level": g.apply(lambda x: ((1 - x.vsA) * x.w).sum())})
m = m.sort_values("pts_if_B=A_level", ascending=False)
pd.set_option("display.width", 200)
print(m.round(3).head(25).to_string())
v = t[t.val.notna()]
for c in ("B", "combo3"):
    sc = pd.Series(item_scores(v[c], v.val), index=v.index)
    print(c, "val by category", sc.groupby(v.category).mean().round(3).to_dict())
    print("   val by subset", sc.groupby(v.subset).mean().round(3).to_dict())
m.to_csv(OUT / "trackb_map.csv")
