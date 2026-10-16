"""Collect the lab family audit (auditor fixes + blind re-measurements) from the workflow journals.

Acceptance rule (fixed before reading the results in bulk): a fix is accepted when the blind re-measurement exists and
(1) moves the same way as the auditor's value relative to the current answer, by at least 15% of the current answer, and
(2) is within a factor 1.35 of the auditor's value. Accepted value = geometric mean(auditor, re-measurement).
Everything else is logged and left unchanged.
    .venv/bin/python research/next/merge/collect_labaudit.py JOURNAL [JOURNAL ...]
"""
import json, math, sys
from pathlib import Path
import pandas as pd
rows = []
for jp in sys.argv[1:]:
    for line in open(jp):
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("type") != "result":
            continue
        r = d.get("result") or d.get("value")
        if isinstance(r, str):
            try:
                r = json.loads(r)
            except Exception:
                continue
        if not isinstance(r, dict):
            continue
        if "fixes" in r:  # auditor
            for f in r["fixes"]:
                rows.append(dict(kind="fix", qid=int(f["qid"]), current=f["current"], value=f["new_value"], note=f["why_current_wrong"][:300]))
        elif "measurements" in r:
            for m in r["measurements"]:
                rows.append(dict(kind="meas", qid=int(m["qid"]), value=m["value"], note=m.get("confidence", "")))
df = pd.DataFrame(rows)
fx = df[df.kind == "fix"].drop_duplicates("qid", keep="last").set_index("qid")
ms = df[df.kind == "meas"].drop_duplicates("qid", keep="last").set_index("qid")
out = []
for q, f in fx.iterrows():
    cur, a = float(f.current), float(f.value)
    b = float(ms.value[q]) if q in ms.index else math.nan
    ok = (not math.isnan(b) and b > 0 and math.copysign(1, a - cur) == math.copysign(1, b - cur)
          and abs(b - cur) >= 0.15 * cur and max(a, b) / min(a, b) <= 1.35)
    out.append(dict(qid=q, current=cur, auditor=a, remeasure=b, accepted=ok, value=math.sqrt(a * b) if ok else math.nan,
                    conf=ms.note.get(q, "") if q in ms.index else "", why=f.note))
res = pd.DataFrame(out)
res.to_csv(Path(__file__).with_name("labaudit_fixes.csv"), index=False)
pd.set_option("display.width", 220); pd.set_option("display.max_colwidth", 60)
print(res.round(3).to_string())
print("proposed", len(res), "accepted", int(res.accepted.sum()))
