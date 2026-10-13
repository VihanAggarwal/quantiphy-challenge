"""EVALUATION ONLY: per subset, score the method variants on the 128 test rows that overlap validation questions
(validation labels attached by video+question text). Variants: base (physb2), raw geometry, raw direct (run 1),
gm(geo, direct1), median of the 3 direct runs (3D non-lab only), gm(geo, med3).
Video-clustered bootstrap CI of (variant - base)."""
from common import *

t = pd.read_pickle(OUT / "table.pkl")
v = t[t.overlap & t.val.notna()].copy()
v["med3"] = np.exp(np.log(v[["d1", "d2", "d3"]]).median(axis=1, skipna=True))
v["gm"] = np.sqrt(v.r_geo_value * v.d1)
v["gm_med3"] = np.sqrt(v.r_geo_value * v.med3)
cols = ["base", "r_geo_value", "d1", "gm", "med3", "gm_med3"]
for c in cols:
    ok = v[c].notna() & (v[c] > 0)
    v["s_" + c] = np.where(ok, item_scores(v[c].where(ok, 1.0), v.val), np.nan)
pd.set_option("display.width", 250)
rows = []
for key, g in list(v.groupby("sub")) + list(v.groupby(v.category + ":" + v.srcg)) + list(v.groupby("category")):
    r = dict(sub=key, n=len(g), vids=g.video_id.nunique())
    for c in cols:
        r[c] = g["s_" + c].mean()
    for c in cols[1:]:
        gg = g[g["s_" + c].notna()]
        if len(gg) >= 3:
            m, lo, hi = clustered_boot(gg["s_" + c] - gg.s_base, gg.video_id)
            r[c + "_d"] = f"{m:+.3f} [{lo:+.3f},{hi:+.3f}]"
    rows.append(r)
res = pd.DataFrame(rows)
print(res.round(3).to_string())
res.to_csv(OUT / "val_methods.csv", index=False)
