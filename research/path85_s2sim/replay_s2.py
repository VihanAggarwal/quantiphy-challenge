"""Replay the cached Claude run (refine + dense motion from cache, as in the test run) for 2D simulation clips and
keep each question's annotation + geometry debug (scale, target px). No API calls.
    ANTHROPIC_API_KEY="" ANTHROPIC_BASE_URL="http://127.0.0.1:9" QP_LEDGER=/tmp/p85.jsonl python replay_s2.py"""
import pickle, sys
from pathlib import Path
HERE = Path(__file__).parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
import pandas as pd
import run_claude as rc
from qp.data import load_split
from qp.geometry import solve

df = load_split("test")
df = df[df.video_id.str.startswith("simulation") & df.video_type.str[1].eq("2")]
records = rc.load_records(ROOT / "runs/test_v1_high_854/test/records")
records = {k: v for k, v in records.items() if k in set(df.video_id)}
anns = rc.annotations(df, records, refine_priors=True, dense="motion",
                      dense_cache=ROOT / "runs/_dense_cache/test", dense_workers=2)
recs = rc.prepare_records(df, records)
out = {}
for r in df.itertuples():
    a = anns.get(int(r.qid)); rec = recs.get(r.video_id, {})
    if a is None or not rec.get("meta"):
        continue
    m = rec["meta"]
    ans = solve(a.spec, a.tracks, tuple(m["image_size"]), float(m["fps"]), seen_scale=float(m.get("scale") or 1.0))
    out[int(r.qid)] = dict(video_id=r.video_id, spec=a.spec, tracks=a.tracks, value=ans.value, flags=ans.flags,
                           debug=ans.debug, image_size=tuple(m["image_size"]), fps=float(m["fps"]),
                           seen=float(m.get("scale") or 1.0))
with open(HERE / "out/replay_s2.pkl", "wb") as fh:
    pickle.dump(out, fh)
run = pd.read_csv(ROOT / "runs/test_v1_high_854/test.csv").set_index("id")
ok = sum(1 for q, o in out.items() if o["value"] is not None and abs(o["value"] / run.geo_value.get(q, float("nan")) - 1) < 1e-6)
print(f"replayed {len(out)} questions; geometry equal to the run's geo_value: {ok}")
