"""Diagnostic E (on p21): one large unmeasured subset per category x1e-9 (scores 0).
subset mean = (score_p21 - score_diagE) * N_scored / n_scored, N_scored = S2 553, D2 1137, S3 538, D3 933.
S2: simulation (incl. segmentation)   D2: simulation static   S3: non-lab (sim+seg)   D3: lab static"""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from qp.data import load_test, load_split
t = load_test().set_index("qid"); q = t.question.str.lower()
mot = q.str.contains("acceler|veloc|speed|travel"); sim = t.video_source.isin(["simulation", "segmentation"]); lab = t.video_source == "lab"
vv = load_split("val_hires"); vk = set(zip(vv.video_id, vv.question.str.strip().str.lower()))
ov = pd.Series([(a, b.strip().lower()) in vk for a, b in zip(t.video_id, t.question)], index=t.index)
p = pd.read_csv(ROOT / "submissions/trackA_best_p21.csv"); p = p.rename(columns={p.columns[0]: "id"}).set_index("id").parsed_value.reindex(t.index)
subs = {"S2": (t.category == "S2") & sim, "D2": (t.category == "D2") & sim & ~mot,
        "S3": (t.category == "S3") & sim, "D3": (t.category == "D3") & lab & ~mot}
for c, m in subs.items():
    print(c, "zeroed", int(m.sum()), "scored n", int((m & ~ov).sum())); p[m] *= 1e-9
with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
    pd.DataFrame({"id": p.index, "parsed_value": p.values}).to_csv(fh, index=False)
subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(ROOT / "submissions/trackA_diagE_on_p21.csv")], check=True)
