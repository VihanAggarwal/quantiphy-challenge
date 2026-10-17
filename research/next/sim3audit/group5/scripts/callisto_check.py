# simulation_0195: own Callisto track (frames 0 and 90 = t=0, t=3s) + Jupiter centre; scan f and check
# |P0-J| = |P90-J| = R and chord |P90-P0| = arc consistent with speed 0.627 m/s.
import cv2, numpy as np
cap = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0195.mp4')
fr = []
while True:
    ok, f = cap.read()
    if not ok: break
    fr.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32))
def blob(g, x0, x1, y0, y1, thr):
    sub = g[y0:y1, x0:x1]; bgv = np.median(sub)
    m = sub > bgv + thr
    n, lab, st, cen = cv2.connectedComponentsWithStats(m.astype(np.uint8))
    k = 1 + np.argmax(st[1:, 4])
    ys, xs = np.where(lab == k)
    w = (sub - bgv).clip(0) * (lab == k)
    return x0 + (xs * w[ys, xs]).sum() / w[ys, xs].sum(), y0 + (ys * w[ys, xs]).sum() / w[ys, xs].sum(), st[k], bgv
# Jupiter
g = fr[0]
m = (g > np.median(g) + 15).astype(np.uint8)
n, lab, st, cen = cv2.connectedComponentsWithStats(m)
k = 1 + np.argmax(st[1:, 4])
print('Jupiter bbox', st[k], 'centroid', cen[k], 'eq diam', 2*np.sqrt(st[k][4]/np.pi))
J_px = cen[k]
tr = {}
for i in range(len(fr)):
    gg = fr[i]
    m = (gg > np.median(gg) + 12).astype(np.uint8)
    m[300:700, 780:1100] = 0  # mask jupiter
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n < 2: continue
    kk = 1 + np.argmax(st[1:, 4])
    tr[i] = (cen[kk][0], cen[kk][1], st[kk][2], st[kk][3], st[kk][4])
for i in [0, 30, 60, 90, 99]: print('Callisto', i, np.round(tr[i], 2), 'eq diam', round(2*np.sqrt(tr[i][4]/np.pi), 2))
c = np.array([960., 540.])
R_exp = None
for f in [2400, 2500, 2600, 2650, 2667, 2700, 2800, 2900]:
    ray = lambda p: (lambda d: d / np.linalg.norm(d))(np.array([p[0]-c[0], p[1]-c[1], f]))
    J = 16.549 * ray(J_px); P0 = 13.004 * ray(tr[0][:2]); P90 = 13.856 * ray(tr[90][:2])
    R0 = np.linalg.norm(P0 - J); R90 = np.linalg.norm(P90 - J); ch = np.linalg.norm(P90 - P0)
    Rm = 0.5 * (R0 + R90); arc = 0.627 * 3.0; ch_exp = 2 * Rm * np.sin(arc / (2 * Rm))
    print(f'f={f}: R0={R0:.3f} R90={R90:.3f} chord={ch:.3f} chord_expected_from_speed={ch_exp:.3f}')
np.save('/home/user/quantiphy-challenge/research/next/sim3audit/group5/callisto_track.npy', np.array([[i, *tr[i]] for i in sorted(tr)]))
