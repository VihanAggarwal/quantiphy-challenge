# Route 2 for simulation_0201: per-frame range from drop width (anchored to 0.156 m at t=0 and checked vs 0.186 at t=0.1),
# f scanned; 3D positions along pixel rays; fit s(t) quadratic; choose f giving a = 9.7.
import json, numpy as np
import cv2
tr = json.load(open('/home/user/quantiphy-challenge/research/next/sim3audit/group5/drop_track.json'))
# subpixel width: horizontal extent from the soft difference mask, measured as area/ (vertical extent) is shape dependent;
# use per-row max width of the binary mask via second-moment: width_eff = 4*sqrt(var_x)
cap = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0201.mp4')
fr = []
while True:
    ok, f = cap.read()
    if not ok: break
    fr.append(f)
bg = np.median(np.stack(fr[11:14]).astype(np.float32), 0)
W = []
for t in tr:
    i = t['i']
    d = np.abs(fr[i].astype(np.float32) - bg).sum(2)
    d = cv2.GaussianBlur(d, (5, 5), 0)
    m = d > 30
    sub = m[t['y0']:t['y1'], t['x0']:t['x1']]
    rows = sub.sum(1)
    W.append([t['w'], np.percentile(rows, 95), rows.max(), 4*np.sqrt(np.var(np.where(sub)[1]))])
W = np.array(W, float)
print('widths (bbox, p95 row, max row, 4sigma):')
for t, w in zip(tr, W): print(t['i'], w)
cx = cy = 1280.0
u = np.array([t['cx'] for t in tr]); v = np.array([t['cy'] for t in tr])
tt = np.array([t['i'] for t in tr]) / 60.0
for col, name in [(0, 'bbox'), (2, 'maxrow'), (3, '4sig')]:
    w = W[:, col]
    r = 0.156 * w[0] / w
    print(name, 'range at frame 6 from width:', round(r[6], 4), '(given 0.186)')
    # anchored on both: use r = 0.156*w0/w but rescale exponent? keep simple
    res = []
    for f in np.arange(2500, 6001, 25):
        d = np.stack([(u - cx) / f, (v - cy) / f, np.ones_like(u)], 1)
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        P = d * r[:, None]
        # project onto best-fit line direction
        c = P.mean(0); U, S, Vt = np.linalg.svd(P - c); g = Vt[0]
        if g[1] < 0: g = -g
        s = (P - c) @ g
        A = np.stack([np.ones_like(tt), tt, 0.5 * tt**2], 1)
        coef, *_ = np.linalg.lstsq(A[:8], s[:8], rcond=None)
        res.append((f, coef[2], coef[1] , g))
    res = np.array([(a, b, c) for a, b, c, _ in res])
    k = np.argmin(np.abs(res[:, 1] - 9.7))
    f, a, v0 = res[k]
    print(name, 'f for a=9.7:', f, 'v0 at t=0 (inst):', round(v0, 4))
    for T in [0.05, 0.1, 0.2]:
        print('   t=%.2f backward v=%.3f' % (T, v0 + 9.7 * (T - 1 / 120)))
