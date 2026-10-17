"""merge3 = merge2 + (a) the 10 lab-audit fixes whose blind re-measurement was cut off by the weekly agent limit (auditor
value; all 20 re-measured fixes had agreed) + (b) auditor near-miss notes with two-route evidence:
2852 0054as white ball v(1.5) 3.19 -> 4.748 (same ball/time as accepted 2875/2887/2899; 1.44x low),
2683/2689/2695 0037 glass jar 10.65/10.21 -> 9.1 (two views; ToF reads through the glass),
2703/2710/2717 0038 displacement 0.9-1.4 s 17.3 -> 20.2 (four depth models agree),
2335 0018x box width 9 -> 7.85 (renders share the label; s render fix accepted at 7.85).
    .venv/bin/python research/next/merge/build_merge3.py
"""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[3]
t = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
d = pd.read_csv(ROOT / "submissions/trackA_cand_next_merge2.csv")
cur = d.set_index(d.columns[0]).parsed_value.astype(float).reindex(t.index)
fx = pd.read_csv(Path(__file__).with_name("labaudit_fixes.csv"))
un = fx[~fx.accepted & fx.remeasure.isna()]
new = dict(zip(un.qid.astype(int), un.auditor.astype(float)))
new.update({2852: 4.748, 2683: 9.1, 2689: 9.1, 2695: 9.1, 2703: 20.2, 2710: 20.2, 2717: 20.2, 2335: 7.85})
q = pd.Index(sorted(new))
assert t.srcg.reindex(q).eq("lab").all() and t.fact.reindex(q).isna().all()
out = cur.copy(); out[q] = [new[i] for i in q]
log = pd.DataFrame({"qid": q, "video": t.video_id[q], "cat": t.category[q], "q": t.question[q].str[:60], "old": cur[q], "new": out[q]})
print(log.round(3).to_string()); log.to_csv(Path(__file__).with_name("changes_merge3.csv"), index=False)
with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
    pd.DataFrame({"id": out.index, "parsed_value": out.values}).to_csv(fh, index=False)
subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(ROOT / "submissions/trackA_cand_next_merge3.csv")], check=True)
