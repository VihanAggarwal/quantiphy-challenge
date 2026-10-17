# Ball diameter from a linear chroma channel Y=(R+G)/2-B minus median background; per-ray half-crossing of the local
# interior level (sampled 3-6 px inside the edge), then circle fit. Shadows (grey) barely change Y.
import cv2, numpy as np, sys, json
vid, trk = sys.argv[1], sys.argv[2]; rmax = float(sys.argv[3]); fr_rng = sys.argv[4] if len(sys.argv) > 4 else None
tr = dict((i, r) for i, r in json.load(open(trk)))
c = cv2.VideoCapture(vid); frames = []
while True:
    ok, f = c.read()
    if not ok: break
    f = f.astype(np.float32); frames.append((f[..., 2] + f[..., 1]) / 2 - f[..., 0])
bg = np.median(np.stack(frames[::2]), axis=0)
angs = np.deg2rad(np.arange(0, 360, 6)); out = []
a0, a1 = (int(x) for x in fr_rng.split(',')) if fr_rng else (0, 10**9)
for i, Y in enumerate(frames):
    r = tr.get(i)
    if r is None or not (a0 <= i <= a1): continue
    cx, cy = r['cx'], r['cy']
    if cx < rmax + 3 or cx > Y.shape[1] - rmax - 3 or cy < rmax + 3 or cy > Y.shape[0] - rmax - 3: continue
    d = Y - bg; R = rmax / 2.4
    for it in range(3):
        rr = np.arange(0, rmax, 0.2); P = []
        for a in angs:
            xs = (cx + rr * np.cos(a)).astype(np.float32); ys = (cy + rr * np.sin(a)).astype(np.float32)
            pr = cv2.remap(d, xs.reshape(1, -1), ys.reshape(1, -1), cv2.INTER_LINEAR)[0]
            inn = np.median(pr[(rr > R - 6) & (rr < R - 3)])
            if inn < 10: continue
            th = inn / 2; above = np.nonzero(pr > th)[0]
            above = above[rr[above] < R + 6]
            if len(above) == 0: continue
            k = above[-1]
            if k + 1 >= len(pr): continue
            t = rr[k] + 0.2 * (pr[k] - th) / max(pr[k] - pr[k + 1], 1e-6)
            P.append((cx + t * np.cos(a), cy + t * np.sin(a)))
        P = np.array(P)
        A = np.c_[2 * P[:, 0], 2 * P[:, 1], np.ones(len(P))]; b = (P ** 2).sum(1)
        s = np.linalg.lstsq(A, b, rcond=None)[0]; cx, cy = s[0], s[1]; R = np.sqrt(s[2] + cx ** 2 + cy ** 2)
    res = np.hypot(P[:, 0] - cx, P[:, 1] - cy) - R
    out.append((i, 2 * R, cx, cy, np.sqrt(np.mean(res ** 2))))
for o in out: print('%d D=%.2f c=(%.2f,%.2f) rms=%.2f' % o)
D = np.array([o[1] for o in out]); print('median D %.2f  mean %.2f  sd %.2f  n=%d' % (np.median(D), D.mean(), D.std(), len(D)))
json.dump(out, open(sys.argv[5] if len(sys.argv) > 5 else '/dev/null', 'w'))
