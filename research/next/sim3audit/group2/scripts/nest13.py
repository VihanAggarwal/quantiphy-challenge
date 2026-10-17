"""Nest fall track in simulation_0013: background = frame 53 above row 1500, frame 0 below; centroid of changed pixels in the
left part of the image. Fits a parabola and prints residuals / step sizes to look for dropped frames."""
import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0013.mp4')
fr = []
while True:
    ok, f = c.read()
    if not ok: break
    fr.append(f[:, :1000].astype(np.int16))
fr = np.array(fr)
bg = fr[53].copy(); bg[1450:] = fr[0][1450:]
rows = []
for i in range(14, 45):
    d = np.abs(fr[i] - bg).max(axis=2)
    m = (d > 35).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    k = 1 + np.argmax(st[1:, 4])
    ys, xs = np.nonzero(lab == k)
    rows.append((i, xs.mean(), ys.mean(), st[k, 1], st[k, 1] + st[k, 3], st[k, 4]))
rows = np.array(rows)
np.save('/home/user/quantiphy-challenge/research/next/sim3audit/group2/nest13.npy', rows)
for r in rows:
    print('%d cx=%.1f cy=%.1f top=%d bot=%d area=%d' % tuple(r))
cy = rows[:, 2]
print('dcy', np.round(np.diff(cy), 1).tolist())
print('ddcy', np.round(np.diff(cy, 2), 1).tolist())
