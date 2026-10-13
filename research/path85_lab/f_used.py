"""Which focal length does qp.geometry use on lab 3D questions (MAP between the 84-deg lab FOV prior and the
question's own prior)? CPU replay of the cached records (no API). Writes out/f_used.csv (qid, f_px, value)."""
import sys, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
os.environ["ANTHROPIC_API_KEY"] = ""; os.environ["ANTHROPIC_BASE_URL"] = "http://127.0.0.1:9"
import pandas as pd
from qp import geometry as G
from qp.data import load_split
import run_claude as rc
from qp import claude_annotate as ca
df = load_split("test"); df = df[(df.video_source == "lab") & df.category.isin(["S3", "D3"])]
recs = rc.load_records(ROOT / "runs/test_v1_high_854/test/records")
recs = {k: v for k, v in recs.items() if k in set(df.video_id)}
recs = rc.prepare_records(df, recs)
anns = ca.load_annotations(recs)
anns = {q: a for q, a in anns.items() if q in set(df.qid)}
rc.post_steps(anns, df, recs, refine_priors=False, dense="motion", dense_cache=ROOT / "runs/_dense_cache/test", dense_workers=1)
rows = []
for r in df.itertuples():
    a = anns.get(int(r.qid))
    if a is None:
        continue
    m = recs[r.video_id]["meta"]; W, H = m["image_size"]
    try:
        ans = G.solve(a.spec, a.tracks, (W, H), float(m["fps"]), camera_fov_deg=ca.LAB_FOV_DEG, seen_scale=float(m.get("scale") or 1.0))
        rows.append(dict(qid=int(r.qid), video=r.video_id, cat=r.category, value=ans.value, f_px=ans.debug.get("f_px"), method=ans.method))
    except Exception as e:  # noqa: BLE001
        rows.append(dict(qid=int(r.qid), video=r.video_id, cat=r.category, err=repr(e)[:80]))
pd.DataFrame(rows).to_csv(Path(__file__).parent / "out/f_used.csv", index=False)
print("done", len(rows))
