"""Candidate: lab prop sizes from Table 6 (table6.py tiers A+B) + teal-notebook width pooled from 0013/0014 (our own
geometry there: flat on the desk) into 0023/0024 (book on the slope, renders spread 6.0-20.8 cm).
Base: submissions/trackA_cand_physb2_on_p21.csv. Only lab S3/D3 size rows change; validation-overlap rows are left as
they are (unscored) except where the rule is the same family-level value (kept consistent; they do not score)."""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]; sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
from qp.data import load_test
import table6 as T6
t = load_test().set_index("qid")
base_f = ROOT / "submissions/trackA_cand_physb2_on_p21.csv"
b = pd.read_csv(base_f); b = b.rename(columns={b.columns[0]: "id"}).set_index("id").parsed_value.astype(float).reindex(t.index)
v = b.copy()
lab3 = (t.video_source == "lab") & t.category.isin(["S3", "D3"])
log = []
for q, r in t[lab3].iterrows():
    m = T6.match(r.video_id, r.question)
    if m is None:
        continue
    tier, val, name = m
    unit = r.target_unit
    val_u = val / 100 if unit == "m" else val * 10 if unit == "mm" else val
    if not np.isclose(v[q], val_u, rtol=1e-9):
        log.append(dict(qid=q, video=r.video_id, cat=r.category, rule="T6" + tier, name=name, old=v[q], new=val_u))
        v[q] = val_u
# notebook width: 0023/0024 "width of the book" -> median of the 0013/0014 notebook-width answers (base values)
src = t.index[t.video_id.str.match(r"captured_001[34][sx]?$") & t.question.str.lower().str.contains(r"width of the (?:note ?book|book)")]
w = float(np.median(b[src]))
for q in t.index[t.video_id.str.match(r"captured_002[34][sx]?$") & t.question.str.lower().str.contains(r"width of the book")]:
    log.append(dict(qid=q, video=t.video_id[q], cat=t.category[q], rule="NBpool", name=f"notebook width pooled 0013/0014 ({len(src)} answers)", old=v[q], new=w))
    v[q] = w
# notebook length: 0023/0024 "length of the book" -> median of all teal-notebook length answers (0014, 0023, 0024)
lsrc = t.index[t.video_id.str.match(r"captured_00(14|23|24)[sx]?$") & t.question.str.lower().str.contains(r"length of the book")]
lm = float(np.median(b[lsrc]))
for q in t.index[t.video_id.str.match(r"captured_002[34][sx]?$") & t.question.str.lower().str.contains(r"length of the book")]:
    if abs(np.log(v[q] / lm)) > 0.03:
        log.append(dict(qid=q, video=t.video_id[q], cat=t.category[q], rule="NBpool", name=f"notebook length pooled 0014/0023/0024 ({len(lsrc)} answers)", old=v[q], new=lm))
        v[q] = lm
L = pd.DataFrame(log)
L["ratio"] = L.new / L.old
pd.set_option("display.width", 200); pd.set_option("display.max_rows", 300)
print(L.round(3).to_string())
print(L.groupby(["cat", "rule"]).size())
L.to_csv(HERE / "out/changes_t6.csv", index=False)
assert ((v != b) <= lab3).all()
out = ROOT / "submissions/trackA_cand_labT6_on_physb2.csv"
with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
    pd.DataFrame({"id": v.index, "parsed_value": v.values}).to_csv(fh, index=False)
subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(out)], check=True)
print("rows changed vs base:", int((~np.isclose(v, b, rtol=1e-9)).sum()), t.loc[~np.isclose(v, b, rtol=1e-9), "category"].value_counts().to_dict())
