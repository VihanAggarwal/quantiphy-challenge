import numpy as np, pandas as pd
d = pd.read_csv("out/segtrack_simulation_0171_segmented.csv")
fps = 24.0
h = (d.c0_y1 - d.c0_y0).to_numpy(float); w = (d.c0_x1 - d.c0_x0).to_numpy(float)
print("bbox h px: min %.0f med %.0f max %.0f; w med %.0f" % (h.min(), np.median(h), h.max(), np.median(w)))
labels_v = {0.5: 1.72, 1: 4.89, 2: 1.86, 3: 1.462}
labels_a = {0.5: 1.801, 1: 1.192, 2: 0.705, 3: 2.634}
pts = {"centroid": (d.c0_cx, d.c0_cy), "boxc": ((d.c0_x0 + d.c0_x1) / 2, (d.c0_y0 + d.c0_y1) / 2),
       "top": ((d.c0_x0 + d.c0_x1) / 2, d.c0_y0), "bottom": ((d.c0_x0 + d.c0_x1) / 2, d.c0_y1),
       "x_only_c": (d.c0_cx, d.c0_cy * 0)}
for sname, sc in [("hmax", 2.2 / h.max()), ("hmed", 2.2 / np.median(h))]:
    print("== scale", sname, sc)
    for pn, (x, y) in pts.items():
        x = np.asarray(x, float) * sc; y = np.asarray(y, float) * sc
        sp = np.r_[np.nan, np.hypot(np.diff(x), np.diff(y)) * fps]
        acc = np.r_[np.nan, np.diff(sp) * fps]
        # also central / smoothed variants
        out = []
        for t in labels_v:
            i = int(round(t * fps))
            out.append(f"t{t}: v {sp[i]:.2f}/{labels_v[t]} a {abs(acc[i]):.2f}/{labels_a[t]} vfwd {sp[i+1]:.2f}")
        print(f"  {pn:9s}", " | ".join(out))
