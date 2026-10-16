"""Merge the verified next-jump levers on top of trackA_probe_agent_sim2agent.csv (2026-10-16).
- nlres (adopt), inet (adopt), accounting (probe): restore stated-sibling facts / PHYSB physical scale / family facts the agent
  build overwrote; on rows where they disagree, per-row median of the three values (all agree in direction).
- labstatic (adopt without F): 25 lab rows; the 4 trashbin-height rows (F) are excluded per the verifier.
- labmot: rejected (not used).
    .venv/bin/python research/next/merge/build_merge1.py
"""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[3]
S = ROOT / "submissions"
t = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
def read(n):
    d = pd.read_csv(S / n); return d.set_index(d.columns[0]).parsed_value.astype(float).reindex(t.index)
base = read("trackA_probe_agent_sim2agent.csv")
cand = {k: read(f"trackA_cand_next_{k}.csv") for k in ("nlres", "inet", "accounting")}
ch = pd.DataFrame({k: v.where(~np.isclose(v, base, rtol=1e-9)) for k, v in cand.items()})
out = base.copy()
m = ch.notna().any(axis=1)
out[m] = np.exp(np.log(ch[m]).median(axis=1, skipna=True))
# internet_0051: physical vs in-clip scale is a coin flip per the verifier (calib_physb mildly favours in-clip) -> keep the agent
m51 = t.video_id.eq("internet_0051")
out[m51] = base[m51]
ls = read("trackA_cand_next_labstatic.csv")
F = [2784, 2792, 2800, 2811]
lm = ~np.isclose(ls, base, rtol=1e-9) & ~t.index.isin(F)
assert not (lm & m).any(), "labstatic overlaps the non-lab levers"
out[lm] = ls[lm]
chg = ~np.isclose(out, base, rtol=1e-9)
print("rows changed:", int(chg.sum()), "| scored:", int((chg & t.scored).sum()))
print(pd.crosstab(t.category[chg], t.srcg[chg]))
assert not (chg & t.fact.notna() & ~np.isclose(out, t.fact.fillna(-1), rtol=1e-6) & np.isclose(base, t.fact.fillna(-1), rtol=1e-6)).any()
pd.DataFrame({"qid": t.index[chg], "video": t.video_id[chg], "category": t.category[chg], "old": base[chg], "new": out[chg]}).to_csv(
    ROOT / "research/next/merge/changes_merge1.csv", index=False)
with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
    pd.DataFrame({"id": out.index, "parsed_value": out.values}).to_csv(fh, index=False)
subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(S / "trackA_cand_next_merge1.csv")], check=True)
