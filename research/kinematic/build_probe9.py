"""Probe 9 = probe 8 + kinematic consistency layer (w=0.5), applied only to rows still equal to the raw pipeline
answer (runs/test_v1_high_854/test.csv), so stated facts, family pooling, ensembles and twin copies stay untouched."""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))
from qp.data import load_split
import kinematic_layer as K

test = load_split("test").set_index("qid")
def read(p):
    d = pd.read_csv(p); return d.rename(columns={d.columns[0]: "id"}).set_index("id")["parsed_value"].astype(float).reindex(test.index)
base = read(ROOT / "submissions/trackA_probe8_p7b_d2fixes_d3labphys.csv")
raw = read(ROOT / "runs/test_v1_high_854/test.csv")
new, log = K.apply(base, K.groups(ROOT / "runs/test_v1_high_854/test/records"), test.target_unit.map(K.unit_factor), 0.5, 0.25)
eligible = pd.Series(np.isclose(base, raw, rtol=1e-9), index=test.index)
out = base.where(~eligible, new)
ch = pd.Series(~np.isclose(out, base), index=test.index)
print("changed", int(ch.sum()), test.loc[ch[ch].index, "category"].value_counts().to_dict(),
      "| skipped (family/fact rows):", int((~np.isclose(new, base) & ~eligible).sum()))
r = np.abs(np.log(out[ch] / base[ch])); print("median |log| %.3f, >10%%: %d" % (r.median(), (r > 0.1).sum()))
with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
    pd.DataFrame({"id": out.index, "parsed_value": out.values}).to_csv(fh, index=False)
subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name,
                str(ROOT / "submissions/trackA_probe9_p8_kinematic.csv")], check=True)
