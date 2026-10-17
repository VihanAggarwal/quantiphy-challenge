"""3D-simulation blind sweep inputs: the scored rows of each 3D-sim audit item (research/next/sim3audit/inputs), WITHOUT the current
answer, its provenance or the agent-notes path (the sweep measurer must not be anchored). Stated facts are left out. Current answers
(merge5) and the protected rows (accepted 3D-sim audit fixes) go into the workflow script only, for selecting disagreements.

    .venv/bin/python research/next/sim3sweep/build_inputs.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
sub = pd.read_csv(ROOT / "submissions/trackA_cand_next_merge5.csv").set_index("id").parsed_value
t = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
ch5 = pd.read_csv(ROOT / "research/next/merge/changes_merge5.csv")
protected = sorted(set(ch5.qid[ch5.src.eq("sim3audit")].astype(int)))
items, cur = [], {}
(OUT / "inputs").mkdir(exist_ok=True)
for f in sorted((ROOT / "research/next/sim3audit/inputs").glob("*.json")):
    d = json.loads(f.read_text())
    rows = []
    for r in d["rows"]:
        q = r["qid"]
        fact = t.fact.get(q)
        if pd.notna(fact) and np.isclose(sub[q], fact, rtol=1e-6):
            continue
        rows.append({k: r[k] for k in ("qid", "video_id", "video_path", "category", "question", "prior", "depth_info", "target_unit", "fps")})
        cur[str(q)] = round(float(sub[q]), 5)
    if rows:
        (OUT / "inputs" / f.name).write_text(json.dumps({"item": d["item"], "family": d["family"], "clips": d["clips"], "rows": rows}, indent=1))
        items.append({"item": d["item"], "n": len(rows)})
print(pd.DataFrame(items).to_string(), sum(i["n"] for i in items), "protected", len(protected))
Path("/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/sim3sweep_args.json").write_text(
    json.dumps({"items": items, "current": cur, "protected": protected}))
