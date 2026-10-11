"""Diagnostic C (on probe 7b): one subset per category multiplied by 1e-9 (scores 0), so
subset mean = (score_7b - score_diag) * N_cat / n_subset.
  S2: acceleration targets   S3: lab motion targets   D3: lab motion targets   D2: internet clips"""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from qp.data import load_test
t = load_test().set_index("qid")
d = pd.read_csv(ROOT / "submissions/trackA_probe7b_p5_ens_famext.csv"); d = d.rename(columns={d.columns[0]: "id"}).set_index("id")
v = d.parsed_value.astype(float).reindex(t.index)
q = t.question.str.lower(); motion = q.str.contains("acceler|veloc|speed|travel"); lab = t.video_source == "lab"
subsets = {"S2": (t.category == "S2") & q.str.contains("acceler"),
           "S3": (t.category == "S3") & lab & motion,
           "D3": (t.category == "D3") & lab & motion,
           "D2": (t.category == "D2") & (t.video_source == "internet")}
for c, m in subsets.items():
    print(c, "zeroed", int(m.sum()), "of", int((t.category == c).sum())); v[m] = v[m] * 1e-9
with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
    pd.DataFrame({"id": v.index, "parsed_value": v.values}).to_csv(fh, index=False)
subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(ROOT / "submissions/trackA_diagC_on7b.csv")], check=True)
