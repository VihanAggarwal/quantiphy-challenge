"""Hyp 1: untimed speed priors -- is the prior object's pixel speed constant over the clip?
Per clip (2D, simulation/segmentation), take the prior track with the most observations, fit position vs
time piecewise (speeds between consecutive obs, smoothed) and report: track span / clip length, speed at start
/ middle / end of the track (from a quadratic fit), path/duration mean. Test inputs only."""
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from common import *

d = pd.read_pickle(ROOT / "research/d2static/out/test_table.pkl")
recs = records("test")
sp = specs(recs)
rows = []
for v, g in d[(d.category.isin(["D2", "S2"])) & d.video_source.isin(["simulation", "segmentation"])].groupby("video_id"):
    meta = recs[v]["meta"]
    fps = float(meta["fps"]); n = meta["n_frames_total"]; sc = meta["scale"]
    best = None
    for q in g.index:
        s = sp.get(q)
        if not s or (s["spec"]["prior"]["kind"] not in ("speed", "acceleration")):
            continue
        for tr in s["tracks"]:
            if tr["role"] != "prior":
                continue
            obs = [(o["frame"], o["point"] or ([(o["box"][0] + o["box"][2]) / 2, (o["box"][1] + o["box"][3]) / 2] if o.get("box") else None)) for o in tr["obs"]]
            obs = [(f, p) for f, p in obs if p is not None]
            if best is None or len(obs) > len(best[1]):
                best = (q, obs, s["spec"]["prior"], tr["object"])
    if not best or len(best[1]) < 5:
        continue
    q, obs, prior, obj = best
    f = np.array([o[0] for o in obs], float); P = np.array([o[1] for o in obs], float) / sc
    o = np.argsort(f); f, P = f[o], P[o]
    t = f / fps
    # quadratic fit per coordinate
    c = [np.polyfit(t, P[:, k], 2) for k in range(2)]
    vel = lambda x: np.hypot(*(np.polyval(np.polyder(ck), x) for ck in c))
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    pathv = seg.sum() / (t[-1] - t[0])
    v0, vm, v1 = vel(t[0]), vel((t[0] + t[-1]) / 2), vel(t[-1])
    # 3-segment average speeds
    k = len(t) // 3
    def segv(a, b):
        return np.linalg.norm(np.diff(P[a:b + 1], axis=0), axis=1).sum() / (t[b] - t[a]) if b > a else np.nan
    s1, s2, s3 = segv(0, k), segv(k, 2 * k), segv(2 * k, len(t) - 1)
    rows.append(dict(video_id=v, cat="/".join(sorted(set(g.category))), n_D2static=int(((g.category == "D2") & g.tkind.isin(["size", "distance", "displacement"])).sum()),
                     prior_kind=prior["kind"], prior_time=prior["time"], prior_val=prior["value_si"], obj=obj,
                     fps=fps, n_frames=n, f0=int(f[0]), f1=int(f[-1]), cover=(f[-1] - f[0]) / max(n - 1, 1),
                     v_path=pathv, r_start=v0 / pathv, r_mid=vm / pathv, r_end=v1 / pathv,
                     seg1=s1 / pathv, seg2=s2 / pathv, seg3=s3 / pathv, n_obs=len(t)))
r = pd.DataFrame(rows)
r.to_csv(ROOT / "research/d2static/out/speed_profile.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 400)
print(r.round(3).to_string(index=False))
