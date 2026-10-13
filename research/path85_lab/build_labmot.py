"""Candidate: two lab-motion fixes on physb2 (S3 only, test inputs only).
 (1) BUG: research/labnoise/build_candidate.py protects 'stated-fact' rows by matching the raw number against every
     number in any lab prior text regardless of unit; the 0034a/0034ax right-tennis-ball total path (direct answer
     40 cm) matched the ping-pong prior '40mm' and kept factor 1.0 although the emulator gives 1.52 / 2.50 (capped
     1.6), like every other small-ball path row (0034b: 1.53-1.60). Restore the emulator factor (cap 1.6).
 (2) MULTI-CAMERA: 0034a and 0034b are two cameras of one event with one annotation (identical prior, depth_info and
     question times, so one label per question). Their original-render direct answers are independent estimates of
     the same quantity: pool them (geometric mean of the two originals' direct answers = probe-8 values), then apply
     the median emulator factor of the question's 6 renders (one label -> one answer). Questions asked in both: left/right tennis ball velocity at 1.2 s, total paths."""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]; sys.path.insert(0, str(ROOT))
from qp.data import load_test
t = load_test().set_index("qid")
rd = lambda p: (lambda d: d.rename(columns={d.columns[0]: "id"}).set_index("id").parsed_value.astype(float).reindex(t.index))(pd.read_csv(p))
base = rd(ROOT / "submissions/trackA_cand_physb2_on_p21.csv")
R = pd.read_csv(ROOT / "research/labnoise/out/test_rows_cap1.6.csv").set_index("qid")
fac = R.factor.copy()
# (1) false stated-fact rows: restore min(factor_raw / shade0, 1.6) for the 40-cm right-path rows
bug = R.index[R.stated_fact & (R.kind == "path_length")]
for q in bug:
    fac[q] = min(round(R.factor_raw[q] / R.shade0[q], 3), 1.6)
v = base.copy(); log = []
for q in bug:
    new = R.p8[q] * fac[q]
    log.append(dict(qid=q, video=t.video_id[q], rule="falsefact", old=v[q], new=new)); v[q] = new
# (2) pool 0034a / 0034b direct answers (p8) per shared question
fam = t.video_id.str.replace(r"^(captured_\d+[ab]?)[sxX]?$", r"\1", regex=True)
qn = t.question.str.strip().str.lower()
for qq in sorted(set(qn[fam == "captured_0034a"]) & set(qn[fam == "captured_0034b"])):
    rows = t.index[fam.isin(["captured_0034a", "captured_0034b"]) & (qn == qq)]
    if not R.index.isin(rows).any():
        continue                                   # sizes (already pooled) are not motion rows
    oa = R.p8[[q for q in rows if t.video_id[q] == "captured_0034a"][0]]
    ob = R.p8[[q for q in rows if t.video_id[q] == "captured_0034b"][0]]
    pooled = float(np.sqrt(oa * ob))
    f_med = float(np.median([fac[q] for q in rows]))   # one label per question -> one answer for all 6 renders
    for q in rows:
        new = pooled * f_med
        log.append(dict(qid=q, video=t.video_id[q], rule="pool0034", q=qq[:60], p8a=oa, p8b=ob, old=v[q], new=new)); v[q] = new
L = pd.DataFrame(log); L["ratio"] = L.new / L.old
pd.set_option("display.width", 220); print(L.round(3).to_string())
L.to_csv(HERE / "out/changes_labmot.csv", index=False)
out = ROOT / "submissions/trackA_cand_labmot_on_physb2.csv"
with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
    pd.DataFrame({"id": v.index, "parsed_value": v.values}).to_csv(fh, index=False)
subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(out)], check=True)
ch = ~np.isclose(v, base, rtol=1e-9)
print("rows changed vs base:", int(ch.sum()), t.loc[ch, "category"].value_counts().to_dict())
