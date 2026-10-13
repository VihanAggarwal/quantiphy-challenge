"""Row overlaps (per category) between candidate files and U1-U4, relative to physb2."""
import glob, itertools
from common import *
t = pd.read_pickle(OUT / "table.pkl")
files = sorted(glob.glob(str(SUB / "trackA_cand_*_on_physb2.csv"))) + sorted(glob.glob(str(SUB / "trackA_u[0-9]*.csv")))
ch = {}
for f in files:
    c = read_sub(f).reindex(t.index)
    for cat in N_SCORED:
        s = set(t.index[(~np.isclose(c, t.base, rtol=1e-9)) & (t.category == cat)])
        if s: ch[(Path(f).name.replace("trackA_", "").replace(".csv", ""), cat)] = s
for (a, ca), (b, cb) in itertools.combinations(ch, 2):
    if ca == cb and a != b:
        n = len(ch[(a, ca)] & ch[(b, cb)])
        if n: print(f"{ca}: {a} ({len(ch[(a,ca)])}) x {b} ({len(ch[(b,cb)])}): {n} shared rows")
pd.to_pickle(ch, OUT / "cand_rows.pkl")
