import numpy as np, pandas as pd
d = pd.read_csv("out/segtrack_simulation_0171_segmented.csv")
fps = 24.0
h = (d.c0_y1 - d.c0_y0).to_numpy(float)
x = ((d.c0_x0 + d.c0_x1) / 2).to_numpy(float); y = ((d.c0_y0 + d.c0_y1) / 2).to_numpy(float)
tt = np.arange(len(d)) / fps
lab_v = {0.5: 1.72, 1: 4.89, 2: 1.86, 3: 1.462}; lab_a = {0.5: 1.801, 1: 1.192, 2: 0.705, 3: 2.634}
def smooth_speed(t, hw=0.5):
    m = np.abs(tt - t) <= hw
    px = np.polyfit(tt[m] - t, x[m], 2); py = np.polyfit(tt[m] - t, y[m], 2)
    return np.hypot(px[1], py[1]), np.hypot(2 * px[0], 2 * py[0])
for sname, sc in [("hmax", 2.2 / h.max()), ("hmed", 2.2 / np.median(h)), ("claude~337", 2.2 / 337)]:
    out = []
    for t in lab_v:
        i = int(round(t * fps))
        v_pf = np.hypot(x[i] - x[i - 1], y[i] - y[i - 1]) * fps * sc
        vs, as_ = smooth_speed(t)
        # 3-frame smoothed backward diff
        v3 = np.hypot(x[i] - x[i - 3], y[i] - y[i - 3]) * fps / 3 * sc
        out.append(f"t{t}: pf {v_pf:.2f} b3 {v3:.2f} sm {vs*sc:.2f} lab {lab_v[t]}")
    print(sname, " | ".join(out))
# speed profile per frame (hmax)
sc = 2.2 / h.max()
sp = np.r_[np.nan, np.hypot(np.diff(x), np.diff(y)) * fps * sc]
print(np.round(sp[:80], 2))
print("h:", h[::4].astype(int))
