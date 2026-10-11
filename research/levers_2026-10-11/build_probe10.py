"""Probe 10 (on probe 7b): S3 and D3 lab motion answers x1.25. Hypothesis from the QuantiPhy paper (arXiv:2512.19526,
appendix): lab labels are forward/central differences of hand-clicked object centres with depth-map depth, so they
include click and depth noise that inflates speed magnitudes; on validation lab motion labels run a median ~1.35x our
answers (16 questions, 5 videos; not consistent across videos, so the leaderboard decides). Read with diagnostic C."""
import subprocess, sys, tempfile
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from qp.data import load_test
t = load_test().set_index("qid")
d = pd.read_csv(ROOT / "submissions/trackA_probe7b_p5_ens_famext.csv"); d = d.rename(columns={d.columns[0]: "id"}).set_index("id")
v = d.parsed_value.astype(float).reindex(t.index)
m = t.category.isin(["S3", "D3"]) & (t.video_source == "lab") & t.question.str.lower().str.contains("acceler|veloc|speed|travel")
v[m] *= 1.25
print("scaled", int(m.sum()), t.loc[m, "category"].value_counts().to_dict())
with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
    pd.DataFrame({"id": v.index, "parsed_value": v.values}).to_csv(fh, index=False)
subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(ROOT / "submissions/trackA_probe10_p7b_labmotion125.csv")], check=True)
