"""Ball 3D track (x render, cross-checked on s render): centre x = mid of horizontal extent at the blob's centre row,
centre y = top edge + radius (bottom edge blends into the table). Depth models:
 M1 constant range 0.716 (stated at 1.4 s), M2 table plane s=1 (centre 2 cm above table), M3 plane rescaled so range(1.4 s)=0.716,
 M4 plane s=1.053 (card ToF/plane ratio)."""
import cv2, numpy as np
B = '/home/user/quantiphy-challenge/research/next/labaudit/0038'
F, CX, CY = 711.0, 640.0, 360.0
pl = np.load(f'{B}/plane.npy'); n, d0 = pl[:3], pl[3]
def ray(u, v):
    r = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return r / np.linalg.norm(r)
def track(tag):
    fr = np.load(f'{B}/frames/{tag}.npy').astype(int); med = np.median(fr, axis=0)
    out = []
    for i in range(len(fr)):
        d = np.abs(fr[i] - med).sum(-1)
        m = (d > 45).astype(np.uint8); m[:300] = 0; m[650:] = 0
        if tag == 'o': m[:, :250] = 0
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        nl, lab, st, cen = cv2.connectedComponentsWithStats(m)
        k = 1 + np.argmax(st[1:, 4])
        ys, xs = np.nonzero(lab == k)
        top = ys.min()
        # horizontal extent in the band top+12..top+28 (ball body, below highlights, above shadowed bottom)
        band = (ys >= top + 12) & (ys <= top + 28)
        xl = np.percentile(xs[band], 1); xr = np.percentile(xs[band], 99)
        out.append((i, (xl + xr) / 2, top, xr - xl))
    return np.array(out, float)
def pos(u, top, model, s=1.0):
    # iterate: radius in px depends on range
    rng = 0.72
    for _ in range(5):
        Rpx = 0.02 * F / rng; v = top + Rpx
        r = ray(u, v)
        if model == 'const': rng = 0.716 + 0.02
        else: rng = s * (d0 - 0.02) / (n @ r)
    return rng * r, rng, v
res = {}
for tag in ('x', 's'):
    T = track(tag); res[tag] = T
np.save(f'{B}/track_xs.npy', np.stack([res['x'], res['s']]))
T = res['x']
for i in range(17, 49):
    print(int(T[i, 0]), f'u {T[i,1]:.1f}  top {T[i,2]:.0f}  w {T[i,3]:.1f} | s-render u {res["s"][i,1]:.1f} top {res["s"][i,2]:.0f}')
# scale for M3: plane range at t=1.4
def interp(T, fidx):
    return np.interp(fidx, T[:, 0], T[:, 1]), np.interp(fidx, T[:, 0], T[:, 2])
u14, t14 = interp(T, 33.6)
_, r14, _ = pos(u14, t14, 'plane', 1.0)
s3 = (0.716 + 0.02) / r14
print(f'\nplane range of ball centre at 1.4 s (s=1): {r14:.4f}; surface range {r14-0.02:.4f} vs stated 0.716 -> s3 {s3:.3f}')
models = [('M1 const', 'const', 1), ('M2 plane s=1', 'plane', 1.0), ('M3 plane s->0.716', 'plane', s3), ('M4 plane s=1.053', 'plane', 1.053)]
for tag in ('x', 's'):
    T = res[tag]
    print(f'\n== render {tag}')
    for name, mod, s in models:
        P = np.array([pos(T[i, 1], T[i, 2], mod, s)[0] for i in range(len(T))])
        # speeds per frame step
        st = np.linalg.norm(np.diff(P, axis=0), axis=1)
        # steady segment speeds
        seg1 = np.median(st[18:29]); seg2 = np.median(st[36:48])
        # displacement 0.9 -> 1.4 using video time i/24 and interpolation
        def Pat(fi):
            return np.array([np.interp(fi, T[:, 0], P[:, k]) for k in range(3)])
        dA = np.linalg.norm(Pat(1.4 * 24) - Pat(0.9 * 24))
        dB = np.linalg.norm(Pat(35) - Pat(22.5) ) if False else np.linalg.norm(Pat(34) - Pat(21.5))  # 25-fps original timeline with one dropped frame before (orig j=i+1)
        v14_fwd = np.linalg.norm(Pat(34) - Pat(33)) * 24
        v14_fit = np.linalg.norm(np.polyfit(T[24:34, 0], P[24:34], 1)[0]) * 24
        v14_fit2 = np.linalg.norm(np.polyfit(T[36:48, 0], P[36:48], 1)[0]) * 24
        print(f'  {name:18s} med step f18-29 {seg1*100:.2f} cm, f36-48 {seg2*100:.2f} cm | speed (fit f24-33) {v14_fit*100:.1f} cm/s @24fps, {v14_fit*100*25/24:.1f} @25fps; fit f36-47 {v14_fit2*100:.1f}; fwd f33->34 {v14_fwd*100:.1f}'
              f' | disp 0.9->1.4 (24fps) {dA*100:.2f}  (orig-25fps map) {dB*100:.2f}  range@1.4 {np.linalg.norm(Pat(33.6)):.3f}')
