"""Rows changed per category (scored / overlap) for every candidate built on physb2, plus U1-U4."""
import glob
from common import *
t = pd.read_pickle(OUT / "table.pkl")
files = sorted(glob.glob(str(SUB / "trackA_cand_*_on_physb2.csv"))) + sorted(glob.glob(str(SUB / "trackA_u[0-9]*.csv")))
rows = []
for f in files:
    c = read_sub(f).reindex(t.index)
    ch = ~np.isclose(c, t.base, rtol=1e-9)
    r = dict(file=Path(f).name)
    for cat in N_SCORED:
        m = ch & (t.category == cat)
        r[cat] = int((m & ~t.overlap).sum())
        if m.any():
            r[cat + "_medratio"] = float(np.exp(np.log(c[m] / t.base[m]).median()))
    r["overlap_changed"] = int((ch & t.overlap).sum())
    rows.append(r)
pd.set_option("display.width", 250)
print(pd.DataFrame(rows).round(3).to_string())
