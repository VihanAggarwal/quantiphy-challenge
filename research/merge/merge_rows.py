"""Row-level merge: start from BASE, apply each candidate's rows that differ from REF (the base the candidate was
built on, probe 8), restricted to the listed categories; refuse conflicting edits of one row.

    python research/merge/merge_rows.py OUT BASE REF CAND[:CATS] [CAND[:CATS] ...]     (CATS e.g. S3,D3; default all)
"""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from qp.data import load_test
t = load_test().set_index("qid")
def read(p):
    d = pd.read_csv(p); return d.rename(columns={d.columns[0]: "id"}).set_index("id")["parsed_value"].astype(float).reindex(t.index)
out_path, base, ref = sys.argv[1], read(sys.argv[2]), read(sys.argv[3])
out, owner = base.copy(), {}
for item in sys.argv[4:]:
    path, _, cats = item.partition(":")
    cats = cats.split(",") if cats else ["S2", "D2", "S3", "D3"]
    c = read(path)
    rows = t.index[(~np.isclose(c, ref, rtol=1e-9)) & t.category.isin(cats)]
    for q in rows:
        if q in owner and not np.isclose(out[q], c[q], rtol=1e-9):
            raise SystemExit(f"conflict on qid {q}: {owner[q]} vs {Path(path).name}")
        if not np.isclose(base[q], ref[q], rtol=1e-9) and q not in owner:
            raise SystemExit(f"qid {q}: base already differs from ref, candidate {Path(path).name} would overwrite it")
        out[q] = c[q]; owner[q] = Path(path).name
    print(f"{Path(path).name} [{','.join(cats)}]: {len(rows)} rows {t.loc[rows,'category'].value_counts().to_dict()}")
ch = ~np.isclose(out, base, rtol=1e-12)
print("total changed vs base:", int(ch.sum()), t.loc[ch, "category"].value_counts().to_dict())
with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
    pd.DataFrame({"id": out.index, "parsed_value": out.values}).to_csv(fh, index=False)
subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, out_path], check=True)
