"""Verifier: do any B2route / B1clamp answers equal a Track A (closed-model) answer value for the same question?

Scan 1 (check_b1 style): parsed_value of submissions/trackA_*.csv and research/r86/plan86/trackA_*.csv, on rows that
         differ from B1.
Scan 2 (wider, as B1_verify/closed_scan.py): every numeric column of submissions/trackA_*, research/r86/plan86/*.csv,
         runs/test_*/*.csv (Claude / Sol test runs incl. direct_value) and every research/**/*.csv whose path names a
         closed model or Track A; files must cover >= 300 test qids (validation-only files skipped).
Each match is traced to an open-pipeline origin using the independent rebuild (indep_b2.py): the row's own open member
value, a log-median of 2-4 of its open members, the L4 formula, a clamp bound, or a post-rule value equal to an open raw
value of another row (pool / stated). Also reported for ALL rows (incl. rows unchanged vs B1) as context.
"""
import itertools
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.argv = sys.argv[:1]
sys.path.insert(0, str(Path(__file__).parent))
import indep_b2 as I  # noqa: E402

ROOT, qids, tq = I.ROOT, I.qids, I.tq
SUB = ROOT / "submissions"
B1 = I.sub(SUB / "trackB_cand_B1.csv")
FILES = {"B2route": (I.sub(SUB / "trackB_probe_B2route.csv"), dict(route=("S2", "D2", "S3", "D3"), clamp="b1")),
         "B1clamp": (I.sub(SUB / "trackB_cand_B1clamp.csv"), dict(route=("S2",), clamp="wide"))}


def load_ids(d):
    idc = next((c for c in d.columns if c.lower() in ("id", "qid")), d.columns[0])
    return idc, pd.to_numeric(d[idc], errors="coerce")


# scan 1
s1 = sorted(SUB.glob("trackA_*.csv")) + sorted((ROOT / "research/r86/plan86").glob("trackA_*.csv"))
TA = {}
for f in s1:
    d = pd.read_csv(f)
    idc, ids = load_ids(d)
    TA[str(f.relative_to(ROOT))] = pd.Series(pd.to_numeric(d["parsed_value"], errors="coerce").to_numpy(), index=ids).reindex(qids)
print("scan 1 files:", len(TA))

# scan 2
CLOSED = re.compile(r"trackA|combo|claude|opus|sonnet|gpt|openai|gemini|gem31|argon|_sol|sol_|muse|fable|astra", re.I)
s2 = set(list(SUB.glob("trackA_*.csv")) + list((ROOT / "research/r86/plan86").glob("*.csv"))
         + list((ROOT / "runs").glob("test_*/*.csv"))
         + [p for p in (ROOT / "research").rglob("*.csv") if CLOSED.search(str(p.relative_to(ROOT)))])
vals, nfiles = {}, 0
for f in sorted(s2):
    try:
        d = pd.read_csv(f, low_memory=False)
    except Exception:
        continue
    idc, ids = load_ids(d)
    if ids.isin(qids).sum() < 300:
        continue
    num = [c for c in d.columns if c != idc and pd.api.types.is_numeric_dtype(d[c])
           and c.lower() not in ("fps", "frame", "t", "n", "n_obs", "category")]
    if not num:
        continue
    nfiles += 1
    for c in num:
        for q, v in zip(ids, d[c]):
            if np.isfinite(q) and np.isfinite(v) and v > 0:
                vals.setdefault(int(q), set()).add(float(v))
print("scan 2 files:", nfiles)

pos = pd.Series(np.arange(len(qids)), index=qids)
l4 = I.l4_values()
MEMS = list(I.M)


def explain(q, b, R):
    why = []
    if q in l4.index and np.isclose(b, l4[q], rtol=1e-12):
        why.append("L4 formula")
    mem = [m for m in MEMS if np.isfinite(I.M[m][pos[q]]) and np.isclose(I.M[m][pos[q]], b, rtol=1e-9)]
    if mem:
        why.append("own open member " + "/".join(mem))
    if not why:
        x = {m: I.M[m][pos[q]] for m in MEMS}
        for k in (2, 3, 4):
            for ms in itertools.combinations(MEMS, k):
                v = np.array([x[m] for m in ms])
                v = v[np.isfinite(v) & (v > 0)]
                if len(v) == k and np.isclose(b, np.exp(np.median(np.log(v))), rtol=1e-9):
                    why.append("log-median " + "+".join(ms))
                    break
            if why:
                break
    if q in R["clamp"]:
        why.append("clamp bound")
    if not why and np.isclose(b, R["raw"][q], rtol=1e-9):
        why.append("own routed raw value")
    if not why:
        allraw = R["raw"].dropna().to_numpy()
        if np.isclose(allraw, b, rtol=1e-9).any():
            why.append("pooled: open raw value of another row")
        elif np.isclose(b, R["post"][q], rtol=1e-9):
            why.append("post-rule value (stated / pool)")
    return ", ".join(why) or "UNEXPLAINED"


for name, (s, kw) in FILES.items():
    R = I.build(**kw)
    assert not I.diff(R["final"], s).any(), "independent rebuild must equal the file"
    ch = I.diff(s, B1)
    # scan 1
    hit1 = {q: sum(bool(np.isclose(s[q], a[q], rtol=1e-9)) for a in TA.values()) for q in qids[ch.to_numpy()]}
    hit1 = {q: n for q, n in hit1.items() if n}
    print(f"\n{name}: rows changed vs B1 {int(ch.sum())}")
    print(f"  scan 1 ({len(TA)} Track A parsed_value files): changed rows equal to a Track A value: {len(hit1)}")
    un = []
    for q, n in hit1.items():
        e = explain(q, s[q], R)
        un += [q] if e == "UNEXPLAINED" else []
        print(f"    qid {q} {tq.video_id[q]} {tq.category[q]} {s[q]:.6g} = {e} [in {n} file(s)]")
    print("  scan 1 unexplained:", un or "none")
    # scan 2
    hit2 = [q for q in qids[ch.to_numpy()] if any(np.isclose(s[q], v, rtol=1e-9) for v in vals.get(int(q), ()))]
    un2, kinds = [], {}
    for q in hit2:
        e = explain(q, s[q], R)
        kinds[e.split(" ")[0] + (" " + e.split(" ")[1] if e.startswith("own") else "")] = kinds.get(
            e.split(" ")[0] + (" " + e.split(" ")[1] if e.startswith("own") else ""), 0) + 1
        if e == "UNEXPLAINED":
            un2.append(q)
        if q not in hit1:
            print(f"    scan-2-only qid {q} {tq.video_id[q]} {tq.category[q]} {s[q]:.6g} = {e}")
    print(f"  scan 2 ({nfiles} files, all numeric columns): changed rows equal to a closed value of the same question: "
          f"{len(hit2)} (explanations {kinds}); unexplained: {un2 or 'none'}")
    eq_all = sum(any(np.isclose(s[q], v, rtol=1e-9) for v in vals.get(int(q), ())) for q in qids)
    eq_b1 = sum(any(np.isclose(B1[q], v, rtol=1e-9) for v in vals.get(int(q), ())) for q in qids)
    print(f"  context: all 3289 rows equal to a scan-2 value of the same question: {name} {eq_all}, B1 {eq_b1}")
