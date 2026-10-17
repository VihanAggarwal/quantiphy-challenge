import numpy as np
r = np.load('t59.npy')
fps = 30.0
def fit(sel, sign=-1, deg=2):
    i = r[sel, 0]; t = i / fps
    x = r[sel, 1] + sign * r[sel, 7]; y = r[sel, 2] + sign * r[sel, 8]
    py = np.polyfit(t, y, deg); px = np.polyfit(t, x, deg)
    return py, px
for sign in (-1, 0, 1):
    for a, b in [(66, 97), (66, 81), (81, 97), (70, 95), (66, 90), (75, 97)]:
        sel = (r[:, 0] >= a) & (r[:, 0] <= b)
        py, px = fit(sel, sign)
        print('sign', sign, a, b, 'ay=%.0f px/s2  ax=%.0f' % (2 * py[0], 2 * px[0]))
