"""Like merge_rows.py, but rows where BASE already differs from REF are kept as BASE (skipped, reported) instead of
refusing.  python research/merge/merge_skip.py OUT BASE REF CAND[:CATS] ..."""
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
    skip = [q for q in rows if not np.isclose(base[q], ref[q], rtol=1e-9) and q not in owner]
    for q in rows:
        if q in skip:
            continue
        if q in owner and not np.isclose(out[q], c[q], rtol=1e-9):
            raise SystemExit(f"conflict on qid {q}: {owner[q]} vs {Path(path).name}")
        out[q] = c[q]; owner[q] = Path(path).name
    print(f"{Path(path).name} [{','.join(cats)}]: {len(rows) - len(skip)} rows applied, {len(skip)} kept as base")
ch = ~np.isclose(out, base, rtol=1e-12)
print("total changed vs base:", int(ch.sum()), t.loc[ch, "category"].value_counts().to_dict())
with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
    pd.DataFrame({"id": out.index, "parsed_value": out.values}).to_csv(fh, index=False)
subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, out_path], check=True)
