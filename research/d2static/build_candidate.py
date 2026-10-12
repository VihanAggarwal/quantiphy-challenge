"""Candidate on probe 8: sideways-gravity internet clips (0060-0063) re-solved with rotated tracks
(research/d2static/rotated_gravity.py). Only rows whose probe-8 value is still Claude's direct answer
(no family / fact value) change. Writes submissions/trackA_cand_d2static_rotgrav_on_p8.csv."""
import subprocess, sys, tempfile
import numpy as np
import pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from common import *

OUT = ROOT / "submissions/trackA_cand_d2static_rotgrav_on_p8.csv"
base = pd.read_csv(BASE).set_index("id")["parsed_value"]
raw = pd.read_csv(RAW["test"]).set_index("id")
rot = pd.read_csv(ROOT / "research/d2static/out/rotated_gravity.csv").set_index("qid")
new = base.copy()
log = []
for q, r in rot.iterrows():
    if not (np.isfinite(r.rot) and r.rot > 0):
        continue
    if not np.isclose(base[q], raw.loc[q, "direct_value"], rtol=1e-9):
        log.append((q, "skip: probe-8 value is not the raw direct answer")); continue
    new[q] = r.rot
    log.append((q, f"{base[q]:.4g} -> {r.rot:.4g} ({r.rot / base[q]:.3f})"))
for l in log:
    print(*l)
with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
    new.rename("parsed_value").rename_axis("id").reset_index().to_csv(f.name, index=False)
subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), f.name, str(OUT)], check=True)
cand = pd.read_csv(OUT).set_index("id").parsed_value
chg = pd.Series(~np.isclose(cand, base.reindex(cand.index), rtol=1e-9), index=cand.index)
df = load_split("test").set_index("qid")
print("changed", int(chg.sum()), df.category[chg[chg].index].value_counts().to_dict())
