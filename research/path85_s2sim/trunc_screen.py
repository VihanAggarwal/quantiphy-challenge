"""Truncation screen: 2D-sim speed/acceleration questions at time t whose target is cut by the image border near t
(the visible-part centre lags the object). Uses the annotator's own boxes (no dense step) + the replay's track.
Test inputs only."""
import pickle, sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
import run_claude as rc
from qp.data import load_split
df = load_split("test"); df = df[df.video_id.str.startswith("simulation") & df.video_type.str[1].eq("2")]
records = rc.load_records(ROOT / "runs/test_v1_high_854/test/records")
records = {k: v for k, v in records.items() if k in set(df.video_id)}
anns = rc.annotations(df, records, refine_priors=False, dense="off")
rp = pickle.load(open(HERE / "out/replay_s2.pkl", "rb"))
base = pd.read_csv(ROOT / "submissions/trackA_cand_physb2_on_p21.csv").set_index("id").parsed_value
cat = df.set_index("qid").category
rows = []
for q, o in rp.items():
    sp = o["spec"].target
    if sp.kind not in ("speed", "acceleration") or sp.time is None: continue
    a = anns.get(q)
    if a is None: continue
    tg = [tr for tr in a.tracks if tr.role == "target"]
    if not tg: continue
    W, H = o["image_size"]
    boxes = [(ob.t, ob.box) for ob in tg[0].obs if ob.box]
    if not boxes: continue
    sizes = [max(b[2] - b[0], b[3] - b[1]) for _, b in boxes]
    sz = float(np.median(sizes))
    near = [(t, b) for t, b in boxes if abs(t - sp.time) <= 0.3]
    edge = [min(b[0], b[1], W - b[2], H - b[3]) for _, b in near]
    small = [max(b[2] - b[0], b[3] - b[1]) / sz for _, b in near]
    rows.append(dict(qid=q, video_id=o["video_id"], cat=cat[q], kind=sp.kind, t=sp.time, n_near=len(near),
                     min_edge_px=min(edge) if edge else np.nan, min_rel_size=min(small) if small else np.nan,
                     geo=o["value"], base=base[q]))
d = pd.DataFrame(rows)
d.to_csv(HERE / "out/trunc_screen.csv", index=False)
pd.set_option("display.width", 220)
x = d[(d.min_edge_px < 3) | (d.min_rel_size < 0.75)]
print(len(d), "timed motion rows;", len(x), "with the target cut by the border or shrunk near t")
print(x.round(3).sort_values(["cat", "video_id"]).to_string())
