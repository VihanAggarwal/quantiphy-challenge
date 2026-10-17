"""Gross-outlier family correction: for equivalent questions across a scene family (qp.postprocess.equivalent_questions:
same object/quantity/time, sizes across simulation clips of one family), a row whose answer is more than X times off the
median of the OTHER clips' answers (>= 2 other clips) is set to that median. Held-out check on stated facts: run on answers
where fact rows carry the agent's own answer (not the stated value), score fact rows before/after.
    .venv/bin/python research/next/merge/outlier_pool.py [X]
"""
import sys, math
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from qp import postprocess as pp
from qp.data import load_split
from qp.mra import item_scores
X = float(sys.argv[1]) if len(sys.argv) > 1 else 1.4
t = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
d = pd.read_csv(ROOT / "submissions/trackA_cand_next_merge2.csv"); cur = d.set_index(d.columns[0]).parsed_value.astype(float).reindex(t.index)
test = load_split("test")
df = pp._questions(test, None)
ctx = pp._Ctx(df, pp.FrameCache(pp.DEFAULT_CACHE))
eq = pp.equivalent_questions(ctx, list(t.index))
def correct(vals, rows):
    out = vals.copy(); log = []
    for q in rows:
        if q not in eq: continue
        r, s = ctx.row[q], ctx.spec[q]
        others = {}
        for p in eq[q]:
            v = ctx.row[p].video_id
            if pp.base_id(v) == pp.base_id(r.video_id): continue
            if np.isfinite(vals.get(p, np.nan)) and vals[p] > 0:
                others.setdefault(pp.base_id(v), []).append(math.log(vals[p] * ctx.spec[p].to_si))
        if len(others) < 2: continue
        med = float(np.median([np.mean(x) for x in others.values()]))
        own = math.log(vals[q] * s.to_si)
        if abs(own - med) > math.log(X):
            out[q] = math.exp(med) / s.to_si; log.append((q, r.video_id, r.question[:50], vals[q], out[q], len(others)))
    return out, log
# held-out: fact rows with the agent's raw answer (agent answers file) instead of the stated value
import json, glob, os
ag = {}
for f in glob.glob("/tmp/blind_test/*/answers.json"):
    v = os.path.basename(os.path.dirname(f))
    for k, x in json.load(open(f)).items():
        try: ag[(v, int(k))] = abs(float(x))
        except Exception: pass
a = pd.Series([ag.get((v, i), np.nan) for i, v in zip(t.index, t.video_id)], index=t.index)
fm = t.fact.notna() & a.notna()
held = cur.copy(); held[fm] = a[fm]
new, log = correct(held, list(t.index[fm]))
s0 = item_scores(held[fm].values, t.fact[fm].values); s1 = item_scores(new[fm].values, t.fact[fm].values)
print(f"X={X} facts: {fm.sum()} rows, changed {len(log)}; before {s0.mean():.4f} after {s1.mean():.4f}")
for l in log: print("  ", l[0], l[1], l[2], round(l[3], 3), '->', round(l[4], 3), 'fact', t.fact[l[0]], 'n', l[5])
# apply to all non-fact scored non-lab rows of the current best
nonfact = t.index[t.fact.isna() & t.srcg.ne("lab")]
new2, log2 = correct(cur, list(nonfact))
print(f"non-fact non-lab rows that would change: {len(log2)}")
for l in log2[:60]: print("  ", l[0], l[1], l[2], round(l[3], 3), '->', round(l[4], 3), 'n', l[5])
