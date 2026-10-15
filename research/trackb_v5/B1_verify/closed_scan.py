"""Verifier: do any B1 values that changed vs v3 equal a closed-model (Track A / Claude / Sol / Argon / Gemini / GPT)
answer for the same question? Broader file set than check_b1.py (adds runs/test_*/test.csv incl. direct_value columns
and research/**/ CSVs whose path names a closed model or Track A). Each match is explained from open inputs or listed."""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.argv = ["x"]
sys.path.insert(0, str(Path(__file__).parent))
import indep_b1 as I  # noqa: E402

ROOT = I.ROOT
qids = I.qids
tq = I.tq
B1 = pd.read_csv(ROOT / "submissions/trackB_cand_B1.csv").set_index("id").parsed_value.reindex(qids)
V3 = pd.read_csv(ROOT / "submissions/trackB_v3_catmedian_famrules.csv").set_index("id").parsed_value.reindex(qids)
chg = pd.Series(I.diff(B1, V3), index=qids)

CLOSED = re.compile(r"trackA|combo|claude|opus|sonnet|gpt|openai|gemini|gem31|argon|_sol|sol_|muse|fable|astra", re.I)
files = sorted(set(list((ROOT / "submissions").glob("trackA_*.csv")) + list((ROOT / "research/r86/plan86").glob("*.csv"))
                   + list((ROOT / "runs").glob("test_*/*.csv"))
                   + [p for p in (ROOT / "research").rglob("*.csv") if CLOSED.search(str(p.relative_to(ROOT)))]))
vals = {}   # qid -> set of closed values
nfiles = 0
for f in files:
    try:
        d = pd.read_csv(f, low_memory=False)
    except Exception:
        continue
    idc = next((c for c in d.columns if c.lower() in ("id", "qid")), d.columns[0])
    ids = pd.to_numeric(d[idc], errors="coerce")
    if not ids.isin(qids).mean() > 0.5:
        continue
    num = [c for c in d.columns if c != idc and pd.api.types.is_numeric_dtype(d[c]) and
           c.lower() not in ("fps", "frame", "t", "n", "n_obs", "category")]
    if not num:
        continue
    nfiles += 1
    for c in num:
        for q, v in zip(ids, d[c]):
            if np.isfinite(q) and np.isfinite(v) and v > 0:
                vals.setdefault(int(q), set()).add(float(v))
print("closed-model / Track A files scanned:", nfiles)

raw, post, fin, stated, info = I.build(True, True, True, True, True, True)
pos = pd.Series(np.arange(len(qids)), index=qids)
l4 = I.l4_values()
allraw = np.unique(np.concatenate([raw.dropna().to_numpy(), *[v[np.isfinite(v)] for v in I.M.values()]]))
hits, unexplained = [], []
for q in qids[chg.to_numpy()]:
    b = B1[q]
    if not any(np.isclose(b, v, rtol=1e-9) for v in vals.get(q, ())):
        continue
    why = []
    if q in l4.index and np.isclose(b, l4[q], rtol=1e-12):
        why.append("L4 formula")
    mem = [m for m, v in I.M.items() if np.isfinite(v[pos[q]]) and np.isclose(v[pos[q]], b, rtol=1e-9)]
    if mem:
        why.append("own open member " + "/".join(mem))
    if q in info["clamp"]:
        why.append("clamp bound")
    if not why and np.isclose(allraw, b, rtol=1e-9).any():
        why.append("raw open value of another row (pool)")
    if not why and np.isclose(b, post[q], rtol=1e-9):
        why.append("post-rule value (stated/pool)")
    hits.append((q, tq.video_id[q], tq.category[q], b, ", ".join(why) or "UNEXPLAINED"))
    if not why:
        unexplained.append(q)
for h in hits:
    print("  ", h)
print(f"changed rows {int(chg.sum())}; equal to a closed value of the same question: {len(hits)}; unexplained: {unexplained}")
# same check for ALL B1 rows (incl. unchanged = v3 rows)
eq_all = sum(any(np.isclose(B1[q], v, rtol=1e-9) for v in vals.get(q, ())) for q in qids)
print("all 3289 B1 rows equal to a closed value of the same question (incl. v3-unchanged rows):", eq_all)
