"""PROBE (hypothesis test, not a confident lever): S3 lab label-noise emulator split by scene type.
Validation label / probe-8 answer on lab motion rows (evaluation only): floor events (0034a tennis on the floor,
0061 / 0041 soccer, basketball) median 1.69 (small balls, n=6, 1 event) and 1.42 (mid balls, n=5, 2 events); table-top
events (0013, 0021, 0027) median 1.00 (n=6, 3 events). The leaderboard step sz2 -> sz3 (both scene types up) gave
S3 -0.001 although the emulator model predicted +0.0045: consistent with floor wanting more and table less.
Probe = path85lab (bug fix + 0034 pooling + Table 6) with: S3 floor events (0034a/b, 0035a/b) at the sz 4 cm emulator
factors (0034 questions: pooled 0034a/0034b direct x median factor of the 6 renders), S3 table-top events unchanged
(sz 2 cm). Accelerations / stated facts untouched. Read against path85lab (or physb2 + U1)."""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]; sys.path.insert(0, str(ROOT))
from qp.data import load_test
t = load_test().set_index("qid")
rd = lambda p: (lambda d: d.rename(columns={d.columns[0]: "id"}).set_index("id").parsed_value.astype(float).reindex(t.index))(pd.read_csv(p))
base = rd(ROOT / "submissions/trackA_cand_path85lab_on_physb2.csv")
R4 = pd.read_csv(ROOT / "research/labnoise/out/test_rows_cap1.6_sz0.04.csv").set_index("qid")
R2 = pd.read_csv(ROOT / "research/labnoise/out/test_rows_cap1.6.csv").set_index("qid")
fam = t.video_id.str.replace(r"^(captured_\d+[ab]?)[sxX]?$", r"\1", regex=True)
FLOOR = {"captured_0034a", "captured_0034b", "captured_0035a", "captured_0035b"}
v = base.copy(); log = []
S = R2[(R2.category == "S3") & R2.cls.notna() & ~R2.stated_fact.astype(bool) | (R2.category == "S3") & (R2.kind == "path_length")]
f4 = R4.factor.copy()
for q in R4.index[R4.stated_fact & (R4.kind == "path_length")]:          # same false-fact fix as build_labmot.py
    f4[q] = min(round(R4.factor_raw[q] / R4.shade0[q], 3), 1.6)
qn = t.question.str.strip().str.lower()
for q in S.index:
    if R2.kind[q] == "acceleration":
        continue
    if fam[q] in FLOOR:
        if fam[q] in ("captured_0034a", "captured_0034b") and (qn[q] in set(qn[fam == "captured_0034a"]) & set(qn[fam == "captured_0034b"])):
            rows = t.index[fam.isin(["captured_0034a", "captured_0034b"]) & (qn == qn[q])]
            oa = R2.p8[[x for x in rows if t.video_id[x] == "captured_0034a"][0]]; ob = R2.p8[[x for x in rows if t.video_id[x] == "captured_0034b"][0]]
            new = float(np.sqrt(oa * ob)) * float(np.median([f4[x] for x in rows]))
        else:
            new = R2.p8[q] * f4[q]
    else:
        continue                                   # table-top rows keep the sz 2 cm emulator (validation: its
                                                   # shading-down on radial table rows helped 2/2, 0013 x1.153 hurt)
    if not np.isclose(new, v[q], rtol=1e-9):
        log.append(dict(qid=q, video=t.video_id[q], scene="floor" if fam[q] in FLOOR else "table", kind=R2.kind[q], cls=R2.cls[q], old=v[q], new=new))
        v[q] = new
L = pd.DataFrame(log); L["ratio"] = L.new / L.old
print(L.groupby(["scene", "kind", "cls"]).ratio.agg(["size", "median", "min", "max"]).round(3))
L.to_csv(HERE / "out/changes_floorsplit.csv", index=False)
out = ROOT / "submissions/trackA_cand_s3floorsplit_on_path85lab.csv"
with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
    pd.DataFrame({"id": v.index, "parsed_value": v.values}).to_csv(fh, index=False)
subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(out)], check=True)
ch = ~np.isclose(v, base, rtol=1e-9); print("rows changed vs path85lab:", int(ch.sum()), t.loc[ch, "category"].value_counts().to_dict())
