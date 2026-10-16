"""Soccer vs basketball at rest in ax frame 0-4 (both on the floor beside the sitting person): widest-row widths,
contact rows, and soccer diameter from the basketball (23.2 cm) via floor geometry (camera a height ~0.95 m)."""
import cv2, numpy as np
D = '/home/user/quantiphy-challenge/research/next/labaudit/0054/frames/'
F, CX, CY = 711.0, 640.0, 360.0
f = cv2.imread(D + 'ax_00.png'); b, g, r = [f[..., k].astype(int) for k in range(3)]
hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV).astype(int)
bg = (g > 200) & (r < 80) & (b < 80)
orange = (~bg) & (hsv[..., 0] <= 22) & (hsv[..., 0] >= 2) & (hsv[..., 1] > 90)
# soccer: white or black-patch pixels inside its region; use non-bg and not skin/orange inside a box
def rows_width(m, y0, y1):
    out = []
    for y in range(y0, y1):
        xs = np.nonzero(m[y])[0]
        if len(xs): out.append((y, xs.min(), xs.max(), xs.max() - xs.min() + 1))
    return out
ob = orange.copy(); ob[:, :190] = False; ob[:, 300:] = False; ob[:520] = False
rw = rows_width(ob, 520, 640)
w = max(r_[3] for r_ in rw); ys = [r_[0] for r_ in rw]
print('basketball widest %d px rows %d..%d (height %d)' % (w, min(ys), max(ys), max(ys) - min(ys) + 1))
sm = (~bg) & ((hsv[..., 1] < 60) & (hsv[..., 2] > 120) | (hsv[..., 2] < 70))
sm[:, :120] = False; sm[:, 200:] = False; sm[:560] = False; sm[640:] = False
sm = cv2.morphologyEx(sm.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)).astype(bool)
rw2 = rows_width(sm, 560, 640)
w2 = max(r_[3] for r_ in rw2); ys2 = [r_[0] for r_ in rw2]
print('soccer widest %d px rows %d..%d' % (w2, min(ys2), max(ys2)))
for r_ in rw2[::4]: print(r_)
