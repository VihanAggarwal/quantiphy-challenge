"""Segmented twins share footage and labels with their original clip. Twin rows that still hold the pre-agent base value
(no exact normalised-question match in build_agent_sub) take the original clip's current answer to the EQUIVALENT question
(qp.postprocess.equivalent_questions: same kind/dimension/time/window/axis, matching object names), when the original's
answer came from the agent (differs from the pre-agent base). Stated-fact rows untouched. Writes trackA_cand_next_merge4.csv
on top of merge3.
"""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from qp import postprocess as pp
from qp.data import load_split
t = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
rd = lambda p: (lambda d: d.set_index(d.columns[0]).parsed_value.astype(float).reindex(t.index))(pd.read_csv(ROOT / "submissions" / p))
cur, pre = rd("trackA_cand_next_merge3.csv"), rd("trackA_cand_C1_solS2S3.csv")
df = pp._questions(load_split("test"), None)
ctx = pp._Ctx(df, pp.FrameCache(pp.DEFAULT_CACHE))
twins = [q for q in t.index if t.video_id[q].endswith("_segmented") and np.isclose(cur[q], pre[q]) and pd.isna(t.fact[q])]
eq = pp.equivalent_questions(ctx, twins)
out = cur.copy(); log = []
for q in twins:
    orig = t.video_id[q][: -len("_segmented")]
    cands = [p for p in eq.get(q, []) if t.video_id.get(p) == orig and not np.isclose(cur[p], pre[p])]
    if len(cands) != 1:
        continue
    p = cands[0]
    new = cur[p] * ctx.spec[p].to_si / ctx.spec[q].to_si
    out[q] = new; log.append((q, t.video_id[q], t.category[q], t.question[q][:55], t.question[p][:55], cur[q], new))
L = pd.DataFrame(log, columns=["qid", "video", "cat", "twin_q", "orig_q", "old", "new"])
print(len(twins), "unreplaced twin rows;", len(L), "filled;", L.cat.value_counts().to_dict(), "| scored:", int(t.scored.reindex(L.qid).sum()))
print(L.head(25).round(3).to_string())
L.to_csv(Path(__file__).with_name("changes_twin_fill.csv"), index=False)
with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
    pd.DataFrame({"id": out.index, "parsed_value": out.values}).to_csv(fh, index=False)
subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(ROOT / "submissions/trackA_cand_next_merge4.csv")], check=True)
