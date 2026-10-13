import numpy as np, pandas as pd
d = pd.read_csv("out/segtrack_simulation_0171_segmented.csv")
fps = 24.0
h = (d.c0_y1 - d.c0_y0).to_numpy(float)
x = ((d.c0_x0 + d.c0_x1) / 2).to_numpy(float); y = ((d.c0_y0 + d.c0_y1) / 2).to_numpy(float)
lab_a = {0.5: 1.801, 1: 1.192, 2: 0.705, 3: 2.634}
for sname, sc in [("hmax", 2.2 / h.max()), ("claude", 2.2 / 337)]:
    s = np.r_[np.nan, np.hypot(np.diff(x), np.diff(y)) * fps * sc]
    for k in (1, 2, 3, 4, 6):
        out = []
        for t, a in lab_a.items():
            i = int(round(t * fps))
            j = np.arange(max(1, i - k), min(len(s), i + k + 1))
            sl = np.polyfit(j / fps, s[j], 1)[0]
            out.append(f"{abs(sl):.2f}/{a}")
        print(sname, "k", k, " ".join(out))
