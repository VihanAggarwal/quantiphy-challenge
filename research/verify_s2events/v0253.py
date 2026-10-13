"""Verifier: simulation_0253 box. Re-fit the pipeline's dense target track (replay_s2.pkl, built by the s2sim
study from cached runs; no API) with a constant-acceleration model over several clean windows, and report
per-observation box sizes / border distances near 0.5 s. Test inputs only."""
import pickle, sys
import numpy as np
ROOT = "/home/user/quantiphy-challenge"
sys.path.insert(0, ROOT)
rp = pickle.load(open(f"{ROOT}/research/path85_s2sim/out/replay_s2.pkl", "rb"))
o = rp[855]; sc = o["debug"]["scale_m_per_px"]; W, H = o["image_size"]
tg = [tr for tr in o["tracks"] if tr.role == "target"][0]
rows = []
for ob in tg.obs:
    p = ob.point or ([(ob.box[0] + ob.box[2]) / 2, (ob.box[1] + ob.box[3]) / 2] if ob.box else None)
    rows.append((ob.t, p[0], p[1], ob.box))
rows.sort(key=lambda r: r[0])
T = np.array([r[0] for r in rows]); X = np.array([r[1] for r in rows]); Y = np.array([r[2] for r in rows])
print("scale", sc, "image", W, H, "n obs", len(T), "source", tg.source)
for t_, x, y, b in rows[:12]:
    print(f"  t={t_:.3f} c=({x:.1f},{y:.1f}) box={None if b is None else [round(v) for v in b]}")
# along-path distance (arc length) vs time
s = np.r_[0, np.cumsum(np.hypot(np.diff(X), np.diff(Y)))] * sc
for lo, hi in ((0.6, 1.85), (0.7, 1.85), (0.6, 1.4), (0.8, 1.85), (0.55, 1.85)):
    m = (T >= lo - 1e-9) & (T <= hi + 1e-9)
    c = np.polyfit(T[m], s[m], 2)  # s = c0 t^2 + c1 t + c2
    a = 2 * c[0]; v05 = 2 * c[0] * 0.5 + c[1]
    res = s[m] - np.polyval(c, T[m])
    print(f"window {lo}-{hi}: n={m.sum()} a={a:.3f} v(0.5)={v05:.3f} v(1)={2*c[0]+c[1]:.3f} v(1.5)={3*c[0]+c[1]:.3f} rms resid={res.std()*100:.2f} cm")
# also per-axis quadratic (the pipeline-style vector fit)
m = (T >= 0.6) & (T <= 1.85)
cx = np.polyfit(T[m], X[m], 2); cy = np.polyfit(T[m], Y[m], 2)
vx = 2 * cx[0] * 0.5 + cx[1]; vy = 2 * cy[0] * 0.5 + cy[1]
ax, ay = 2 * cx[0], 2 * cy[0]
print("vector fit 0.6-1.85: v(0.5)=", round(np.hypot(vx, vy) * sc, 3), "|a|=", round(np.hypot(ax, ay) * sc, 3),
      "tangential a=", round((ax * vx + ay * vy) / np.hypot(vx, vy) * sc, 3))
# piecewise speeds early
v = np.hypot(np.diff(X), np.diff(Y)) / np.diff(T) * sc
for a_, b_, vv in zip(T[:-1], T[1:], v):
    if a_ < 1.0: print(f"   {a_:.3f}-{b_:.3f}: {vv:.3f} m/s")
