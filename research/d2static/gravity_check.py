"""Hyp 3 (time base): in 2D clips with a SIZE prior, find tracked objects in free flight (vertical parabola)
and compare their vertical acceleration (scale from the stated size) with g. A time-base error beta shows
as g_meas = 9.8 beta^2. Test inputs only."""
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from common import *

d = pd.read_pickle(ROOT / "research/d2static/out/test_table.pkl")
recs = records("test"); sp = specs(recs)
rows = []
for v, g in d[d.category.isin(["S2", "D2"]) & (d.pkind == "size")].groupby("video_id"):
    m = recs[v]["meta"]; fps = float(m["fps"]); sc = m["scale"]
    # scale m/px from the prior extent
    ks = []
    for q in g.index:
        s = sp.get(q)
        if not s: continue
        val = s["spec"]["prior"]["value_si"]
        for tr in s["tracks"]:
            if tr["role"] != "prior": continue
            L = [np.hypot(*(np.subtract(o["extent"][1], o["extent"][0]))) for o in tr["obs"] if o.get("extent")]
            if L and val:
                ks.append(val / (np.median(L) / sc))
    if not ks: continue
    k = float(np.median(ks))
    seen = set()
    for q in g.index:
        s = sp.get(q)
        if not s: continue
        for tr in s["tracks"]:
            obs = [(o["frame"], o["point"] or ([(o["box"][0] + o["box"][2]) / 2, (o["box"][1] + o["box"][3]) / 2] if o.get("box") else None)) for o in tr["obs"]]
            obs = [(f, p) for f, p in obs if p is not None]
            key = (tr["object"], len(obs))
            if len(obs) < 6 or key in seen: continue
            seen.add(key)
            f = np.array([o[0] for o in obs], float); P = np.array([o[1] for o in obs], float) / sc
            t = f / fps
            cy = np.polyfit(t, P[:, 1], 2); res = P[:, 1] - np.polyval(cy, t)
            cx = np.polyfit(t, P[:, 0], 1); resx = P[:, 0] - np.polyval(cx, t)
            ay = 2 * cy[0] * k
            span = np.ptp(P[:, 1])
            rows.append(dict(video_id=v, q=q, obj=tr["object"], n=len(t), fps=fps, ay=ay, rms=np.sqrt(np.mean(res ** 2)),
                             rmsx=np.sqrt(np.mean(resx ** 2)), span_px=span, prior=g.prior.iloc[0], dur=t[-1] - t[0]))
r = pd.DataFrame(rows)
r.to_csv(ROOT / "research/d2static/out/gravity_check.csv", index=False)
x = r[(r.ay > 5) & (r.ay < 16) & (r.span_px > 30)]
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
print(x.round(3).to_string(index=False))
