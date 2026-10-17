"""merge6 = merge5 + accepted fixes of audit round 3 (2D simulation + internet; research/next/audit3), by the rule of
collect_labaudit.py / build_merge5.py: the blind re-measure moves the same way by >= 15% of the current value and is within
1.35x of the auditor's value; value = geometric mean. Stated-fact rows and earlier audit fixes never change.
    .venv/bin/python research/next/merge/build_merge6.py
"""
import math, subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
ROOT = Path(__file__).resolve().parents[3]
t = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
sn = pd.read_csv(ROOT / "research/next/scored_new.csv").set_index("qid").scored_new.reindex(t.index)
rd = lambda p: (lambda d: d.set_index(d.columns[0]).parsed_value.astype(float).reindex(t.index))(pd.read_csv(ROOT / "submissions" / p))
m5 = rd("trackA_cand_next_merge5.csv")
isfact = t.fact.notna() & np.isclose(m5, t.fact.fillna(-1), rtol=1e-6)
ch5 = pd.read_csv(Path(__file__).with_name("changes_merge5.csv"))
protected = set(ch5.qid[ch5.src.isin(["labaudit2", "sim3audit", "verify-keep"])])
EXCLUDE = set()

AUDIT3 = ["wf_95f90037-064"]
# reuse build_merge5's results()/accept() without running its build
src = Path(__file__).with_name("build_merge5.py").read_text()
ns = {"J": Path("/root/.claude/projects/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/subagents/workflows"),
      "json": __import__("json"), "math": math, "np": np, "pd": pd}
exec(src[src.index("def results"):src.index("SIM3 = ")], ns)
a3, _ = ns["accept"](AUDIT3, "audit3")
out = m5.copy(); log = []
for r in a3[a3.accepted].itertuples() if len(a3) else []:
    q = int(r.qid)
    if isfact.get(q, False) or q in protected or q in EXCLUDE: continue
    if not np.isclose(r.current, m5[q], rtol=2e-2):
        print("WARN current mismatch", q, r.current, m5[q])
    out[q] = r.value; log.append(("audit3", q, m5[q], r.value))
L = pd.DataFrame(log, columns=["src", "qid", "old", "new"])
L["cat"] = t.category.reindex(L.qid).values; L["video"] = t.video_id.reindex(L.qid).values; L["scored"] = sn.reindex(L.qid).values
L.to_csv(Path(__file__).with_name("changes_merge6.csv"), index=False)
a3.to_csv(Path(__file__).with_name("audit3_fixes.csv"), index=False)
print("audit3 proposed/accepted:", len(a3), int(a3.accepted.sum()) if len(a3) else 0)
if len(L):
    print(L.assign(kind=L.video.str.split("_").str[0]).groupby(["kind", "cat"]).size().unstack(fill_value=0))
chg = ~np.isclose(out, m5, rtol=1e-9)
print("rows changed vs merge5:", int(chg.sum()), "scored(new):", int((chg & sn).sum()))
with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
    pd.DataFrame({"id": out.index, "parsed_value": out.values}).to_csv(fh, index=False)
subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(ROOT / "submissions/trackA_cand_next_merge6.csv")], check=True)
