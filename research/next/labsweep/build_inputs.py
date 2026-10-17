"""Lab blind sweep inputs: every scored lab test row per family, WITHOUT the current answer or its provenance (the sweep
measurer must not be anchored). Current answers (merge5) go only to the workflow args, for selecting disagreements.

    .venv/bin/python research/next/labsweep/build_inputs.py   # writes inputs/<family>.json, prints the args JSON path
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
sub = pd.read_csv(ROOT / "submissions/trackA_cand_next_merge5.csv").set_index("id").parsed_value
t = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
items, cur = [], {}
(OUT / "inputs").mkdir(exist_ok=True)
for f in sorted((ROOT / "research/next/labaudit2/inputs").glob("*.json")):
    d = json.loads(f.read_text())
    rows = []
    for r in d["rows"]:
        prov = str(r.get("provenance", ""))
        fact = t.fact.get(r["qid"])
        if pd.notna(fact) and abs(sub[r["qid"]] / fact - 1) < 1e-6:
            continue                                            # stated fact: exact, not measured
        rows.append({k: r[k] for k in ("qid", "video_id", "video_path", "category", "question", "prior", "depth_info",
                                       "target_unit", "fps")})
        cur[r["qid"]] = float(sub[r["qid"]])
    if rows:
        (OUT / "inputs" / f.name).write_text(json.dumps({"family": d["family"], "rows": rows}, indent=1))
        items.append({"family": d["family"], "n": len(rows)})
print(pd.DataFrame(items).to_string(), sum(i["n"] for i in items))
scratch = Path("/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/labsweep_args.json")
scratch.write_text(json.dumps({"families": [i["family"] for i in items], "current": {str(k): v for k, v in cur.items()}}))
print(scratch)
