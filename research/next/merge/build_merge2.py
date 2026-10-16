"""merge2 = merge1 + lab family audit fixes accepted by collect_labaudit.py (blind re-measurement agrees in direction,
>= 15% move, within 1.35x; value = geometric mean of the two measurements).
    .venv/bin/python research/next/merge/build_merge2.py
"""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[3]
t = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
d = pd.read_csv(ROOT / "submissions/trackA_cand_next_merge1.csv")
cur = d.set_index(d.columns[0]).parsed_value.astype(float).reindex(t.index)
fx = pd.read_csv(Path(__file__).with_name("labaudit_fixes.csv"))
acc = fx[fx.accepted]
assert t.srcg.reindex(acc.qid).eq("lab").all(), "audit fixes must be lab rows"
assert np.allclose(cur.reindex(acc.qid).values, acc.current.values, rtol=1e-3), "fix 'current' differs from merge1"
assert t.fact.reindex(acc.qid).isna().all(), "no stated-fact row may change"
out = cur.copy()
out[acc.qid.values] = acc.value.values
chg = ~np.isclose(out, cur, rtol=1e-9)
print("rows changed vs merge1:", int(chg.sum())); print(pd.crosstab(t.category[chg], t.video_id[chg].str[:12]))
with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
    pd.DataFrame({"id": out.index, "parsed_value": out.values}).to_csv(fh, index=False)
subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(ROOT / "submissions/trackA_cand_next_merge2.csv")], check=True)
