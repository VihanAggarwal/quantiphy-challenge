"""Time outside the target track (geometry clamps to the track end): extrapolate a timed SPEED with the local
tangential acceleration at the track edge instead of clamping (2D simulation clips; test inputs only).
v(t) = v(t_e) + (dv/dt)(t_e) * (t - t_e), dv/dt from the geometry's own speeds at t_e and t_e -+ 0.1 s."""
import pickle, sys
from dataclasses import replace
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path("/home/user/quantiphy-challenge/research/path85_s2sim"); ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from qp.geometry import solve
sys.path.insert(0, str(HERE)); from common import test_table
rp = pickle.load(open(HERE / "out/replay_s2.pkl", "rb"))
t = test_table()
rows = []
for q, o in rp.items():
    sp = o["spec"]
    if sp.target.kind != "speed" or sp.target.time is None or "time_outside_track" not in o["flags"] or o["value"] is None:
        continue
    tg = [tr for tr in o["tracks"] if tr.role == "target"]
    T = [ob.t for ob in tg[0].obs]
    lo, hi = min(T), max(T); tq = sp.target.time
    te = hi if tq > hi else lo
    dt = 0.1 if tq > hi else -0.1
    def v_at(x):
        s2 = replace(sp, target=replace(sp.target, time=float(x)))
        a = solve(s2, o["tracks"], o["image_size"], o["fps"], seen_scale=o["seen"])
        return a.value
    ve, vin = v_at(te), v_at(te - dt)
    if ve is None or vin is None: continue
    slope = (ve - vin) / dt
    vnew = ve + slope * (tq - te)
    rows.append(dict(qid=q, video_id=o["video_id"], cat=t.category[q], t=tq, track=(round(lo, 2), round(hi, 2)), gap=round(tq - te, 3),
                     geo=o["value"], v_edge=ve, slope=slope, v_extrap=vnew, base=t.base[q], direct=t.run_direct_value[q]))
d = pd.DataFrame(rows)
d["new_base"] = d.base * d.v_extrap / d.geo
d["ratio"] = d.new_base / d.base
d["direct_closer"] = np.abs(np.log(d.new_base / d.direct)) < np.abs(np.log(d.base / d.direct))
pd.set_option("display.width", 250)
print(d.round(3).to_string())
d.to_csv(Path("/home/user/quantiphy-challenge/research/verify_s2events/extrap_rerun.csv"), index=False)
