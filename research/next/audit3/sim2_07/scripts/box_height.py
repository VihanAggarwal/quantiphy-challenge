# Box extent perpendicular to slope (and along slope) from chroma Y=(R+G)/2-B half-crossings, per frame.
import cv2, numpy as np, json, sys
vid, trk = sys.argv[1], sys.argv[2]
tr = json.load(open(trk))
ang = np.deg2rad(44.25); u = np.array([np.cos(ang), np.sin(ang)]); n = np.array([-u[1], u[0]])
c = cv2.VideoCapture(vid); i = -1; rows = []
while True:
    ok, f = c.read(); i += 1
    if not ok: break
    r = tr[i] if i < len(tr) else None
    if r is None or i < 14 or i == 27: continue
    f = f.astype(np.float32); Y = (f[..., 2] + f[..., 1]) / 2 - f[..., 0]
    Y = cv2.GaussianBlur(Y, (0, 0), 0.7)
    cx, cy = r['cx'], r['cy']; s0 = cx * u[0] + cy * u[1]; t0 = cx * n[0] + cy * n[1]
    H = []
    for ds in np.arange(-25, 26, 5):
        tt = np.arange(-70, 70, 0.25)
        pts = (s0 + ds) * u[None, :] + (t0 + tt)[:, None] * n[None, :]
        pr = cv2.remap(Y, pts[:, 0].astype(np.float32).reshape(1, -1), pts[:, 1].astype(np.float32).reshape(1, -1), cv2.INTER_LINEAR)[0]
        bgv = np.median(np.r_[pr[:20], pr[-20:]]); inn = np.median(pr[(np.abs(tt) < 20)])
        th = (bgv + inn) / 2; ab = np.nonzero(pr > th)[0]
        if len(ab) < 10: continue
        k0, k1 = ab[0], ab[-1]
        tl = tt[k0] - 0.25 * (pr[k0] - th) / max(pr[k0] - pr[k0 - 1], 1e-6)
        tr_ = tt[k1] + 0.25 * (pr[k1] - th) / max(pr[k1] - pr[k1 + 1], 1e-6)
        H.append(tr_ - tl)
    rows.append((i, s0, np.median(H), np.std(H)))
    print('%d s=%.0f height=%.2f (sd %.2f)' % rows[-1])
R = np.array(rows); c1 = np.polyfit(R[:, 1], R[:, 2], 1)
print('height vs s: slope %.5f px/px -> change over 1100 px = %.2f%% of %.1f' % (c1[0], 100 * c1[0] * 1100 / np.mean(R[:, 2]), np.mean(R[:, 2])))
