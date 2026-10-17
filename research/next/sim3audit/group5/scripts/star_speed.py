# simulation_0312: average speed from own per-frame centroid + size-based range, anchored to the given ranges at t=1, 2 s.
import cv2, numpy as np
cap = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0312.mp4')
fr = []
while True:
    ok, f = cap.read()
    if not ok: break
    fr.append(f.astype(np.float32))
bg = np.array([155., 185., 197.])
U, V, Hh = [], [], []
for f in fr:
    d = (bg[0] - f[..., 0]) + (bg[1] - f[..., 1])
    a = np.clip(d / 150, 0, 1); a[a < 0.15] = 0
    ys, xs = np.nonzero(a)
    w = a[ys, xs]
    U.append((xs * w).sum() / w.sum()); V.append((ys * w).sum() / w.sum())
    rows = a.max(1); r = np.where(rows > 0.5)[0]
    # sub-pixel vertical extent via column-summed coverage profile edges
    prof = a.max(1)
    Hh.append(prof.sum())  # soft height in px
U, V, Hh = map(np.array, (U, V, Hh))
fps = 24.0; n = len(U); t = np.arange(n) / fps
k1, k2 = 24, 48
for F in [1428.0, 1459.0]:
    for conv in ['range', 'Z']:
        # depth proxy ~ 1/height; calibrate scale at t=1,2 (least squares through both anchors)
        inv = 1.0 / Hh
        rays = np.stack([(U - 540) / F, (V - 540) / F, np.ones(n)], 1)
        nr = np.linalg.norm(rays, axis=1)
        given = {k1: 6.552, k2: 8.345}
        # depth along optical axis Zc = c * inv ; range = Zc * nr
        cs = [given[k] / (inv[k] * (nr[k] if conv == 'range' else 1.0)) for k in (k1, k2)]
        c = np.mean(cs)
        Zc = c * inv
        P = rays * Zc[:, None]
        # smooth trajectory with a quadratic-in-time per coordinate (cubic) to suppress jitter
        Ps = np.stack([np.polyval(np.polyfit(t, P[:, j], 4), t) for j in range(3)], 1)
        seg = np.linalg.norm(np.diff(Ps, axis=0), axis=1) * fps
        chord = np.linalg.norm(Ps[-1] - Ps[0]) / t[-1]
        print(f'F={F:.0f} {conv:5s}: anchor scale mismatch {cs[0]/cs[1]:.3f}; mean speed {seg.mean():.3f} m/s (min {seg.min():.2f} max {seg.max():.2f}); end-to-end chord/T {chord:.3f}')
