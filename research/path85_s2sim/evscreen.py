"""Event screen on the pipeline's own target tracks (replay_s2.pkl): for each 2D-sim speed/acceleration question at
time t, piecewise px speeds of the target track just before and after t; flags abrupt changes (collisions, jumps,
starts/stops) within +-0.25 s, where the label (one-frame backward difference) and the smoothed fit can differ."""
import pickle, sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from qp.data import load_test
rp = pickle.load(open(HERE / "out/replay_s2.pkl", "rb"))
t = load_test().set_index("qid")
base = pd.read_csv(ROOT / "submissions/trackA_cand_physb2_on_p21.csv").set_index("id").parsed_value
rows = []
for q, o in rp.items():
    sp = o["spec"].target
    if sp.kind not in ("speed", "acceleration") or sp.time is None or t.category[q] not in ("S2", "D2"):
        continue
    tg = [tr for tr in o["tracks"] if tr.role == "target"]
    if not tg: continue
    obs = [(ob.t, ob.point or ([(ob.box[0] + ob.box[2]) / 2, (ob.box[1] + ob.box[3]) / 2] if ob.box else None)) for ob in tg[0].obs]
    obs = sorted([(a, b) for a, b in obs if b is not None])
    if len(obs) < 3: continue
    T = np.array([a for a, _ in obs]); P = np.array([b for _, b in obs], float)
    tq = sp.time
    v = np.hypot(np.diff(P[:, 0]), np.diff(P[:, 1])) / np.diff(T)      # piecewise px/s
    mid = (T[1:] + T[:-1]) / 2
    pre = v[(mid <= tq) & (mid >= tq - 0.3)]; post = v[(mid > tq) & (mid <= tq + 0.3)]
    seg = v[(T[:-1] <= tq + 1e-9) & (T[1:] >= tq - 1e-9)]   # interval(s) containing t (backward side first)
    back = v[(T[1:] <= tq + 1e-9) & (T[1:] >= tq - 0.15)]    # intervals ending at or just before t
    rows.append(dict(qid=q, video_id=o["video_id"], cat=t.category[q], kind=sp.kind, t=tq, src=tg[0].source, nobs=len(obs),
                     geo=o["value"], base=base[q], geo_px=o["debug"].get("target_px"),
                     pre=np.median(pre) if len(pre) else np.nan, post=np.median(post) if len(post) else np.nan,
                     back=np.median(back) if len(back) else np.nan, flags=";".join(o["flags"])))
d = pd.DataFrame(rows)
d["jump"] = np.abs(np.log((d.post + 1) / (d.pre + 1)))
d["back_vs_geo"] = np.log((d.back + 1) / (d.geo_px + 1))
d.to_csv(HERE / "out/evscreen.csv", index=False)
pd.set_option("display.width", 250)
sp = d[d.kind == "speed"]
print(len(d), "rows;", "speed", len(sp), "| jump>0.4:", int((sp.jump > 0.4).sum()), "| |back/geo|>0.3:", int((np.abs(sp.back_vs_geo) > 0.3).sum()))
x = sp[(sp.jump > 0.4) | (np.abs(sp.back_vs_geo) > 0.3)].sort_values("cat")
print(x.round(2).to_string())
