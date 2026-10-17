"""Track tennis (yellow) and white (ping-pong) balls in captured_0031 renders.
Per frame: mask centroid, bbox, and sub-pixel radial-edge circle fit.
Output: ../track_<render>.json
"""
import cv2, numpy as np, json, sys
R = sys.argv[1] if len(sys.argv) > 1 else 'x'
vid = {'o': 'captured_0031', 's': 'captured_0031s', 'x': 'captured_0031x'}[R]
cap = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    frames.append(f)
print(vid, len(frames), cap.get(cv2.CAP_PROP_FPS))


def fit_circle(P):
    A = np.c_[2 * P[:, 0], 2 * P[:, 1], np.ones(len(P))]
    b = (P ** 2).sum(1)
    c = np.linalg.lstsq(A, b, rcond=None)[0]
    return c[0], c[1], np.sqrt(c[2] + c[0] ** 2 + c[1] ** 2)


def edge_fit(g, cx, cy, r0, sign=-1, angs=None):
    """radial profile edge points; sign=-1: bright inside -> dark outside"""
    if angs is None:
        angs = np.linspace(0, 2 * np.pi, 90, endpoint=False)
    pts = []
    for a in angs:
        rs = np.arange(max(2, r0 * 0.5), r0 * 1.6, 0.1)
        xs = cx + rs * np.cos(a); ys = cy + rs * np.sin(a)
        prof = cv2.remap(g, xs.astype(np.float32).reshape(1, -1), ys.astype(np.float32).reshape(1, -1),
                         cv2.INTER_LINEAR).ravel()
        d = np.gradient(prof) * sign
        k = np.argmax(d)
        pts.append((xs[k], ys[k], a))
    pts = np.array(pts)
    P = pts[:, :2]
    keep = np.ones(len(P), bool)
    for _ in range(5):
        x0, y0, r = fit_circle(P[keep])
        dist = np.hypot(P[:, 0] - x0, P[:, 1] - y0) - r
        keep = np.abs(dist) < max(0.8, 2.5 * np.std(dist[keep]))
    x0, y0, r = fit_circle(P[keep])
    up = keep & (np.sin(pts[:, 2]) < 0.2)   # exclude bottom (contact/shadow)
    xu, yu, ru = fit_circle(P[up])
    return dict(cx=x0, cy=y0, d=2 * r, n=int(keep.sum()), cxu=xu, cyu=yu, du=2 * ru)


out = []
prevT = prevW = None
for i, f in enumerate(frames):
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    H, S, V = hsv[..., 0].astype(int), hsv[..., 1].astype(int), hsv[..., 2].astype(int)
    rec = {'i': i}
    # tennis: yellow
    mT = ((H > 20) & (H < 40) & (S > 120) & (V > 90)).astype(np.uint8)
    mT[:380] = 0
    n, lab, st, cen = cv2.connectedComponentsWithStats(mT)
    if n > 1:
        k = 1 + np.argmax(st[1:, 4])
        if st[k, 4] > 50:
            x, y, w, h, a = st[k]
            ys, xs = np.nonzero(lab == k)
            g = cv2.GaussianBlur(f[..., 2].astype(np.float32) * 0 + hsv[..., 1].astype(np.float32), (0, 0), 0.8)
            ef = edge_fit(g, cen[k][0], cen[k][1], max(w, h) / 2, sign=-1)
            rec['T'] = dict(mx=float(cen[k][0]), my=float(cen[k][1]), bx0=int(x), by0=int(y), bw=int(w), bh=int(h),
                            area=int(a), bcx=x + (w - 1) / 2, bcy=y + (h - 1) / 2, **{kk: float(v) for kk, v in ef.items()})
    # white ball: low saturation, bright
    mn = f.min(2).astype(int)
    mW = ((S < 60) & (V > 150) & (mn > 140)).astype(np.uint8)
    mW[:380] = 0; mW[560:] = 0
    if 'T' in rec:  # remove tennis area
        t = rec['T']
        cv2.circle(mW, (int(t['cx']), int(t['cy'])), int(t['d'] / 2 + 3), 0, -1)
    n, lab, st, cen = cv2.connectedComponentsWithStats(mW)
    if n > 1:
        # choose component that is roundish and close to previous
        cands = []
        for k in range(1, n):
            x, y, w, h, a = st[k]
            if a < 40 or w > 80 or h > 80: continue
            fill = a / (w * h)
            score = abs(w / h - 1) + abs(fill - 0.785)
            if prevW is not None:
                score += np.hypot(cen[k][0] - prevW[0], cen[k][1] - prevW[1]) / 30
            cands.append((score, k))
        if cands:
            k = min(cands)[1]
            x, y, w, h, a = st[k]
            g = cv2.GaussianBlur(f.min(2).astype(np.float32), (0, 0), 0.8)
            ef = edge_fit(g, cen[k][0], cen[k][1], max(w, h) / 2, sign=-1)
            rec['W'] = dict(mx=float(cen[k][0]), my=float(cen[k][1]), bx0=int(x), by0=int(y), bw=int(w), bh=int(h),
                            area=int(a), bcx=x + (w - 1) / 2, bcy=y + (h - 1) / 2, **{kk: float(v) for kk, v in ef.items()})
            prevW = (cen[k][0], cen[k][1])
    out.append(rec)
    t = rec.get('T', {}); w = rec.get('W', {})
    print(i, 'T m(%.1f,%.1f) c(%.1f,%.1f) d=%.1f du=%.1f bw=%s bh=%s | W m(%.1f,%.1f) c(%.1f,%.1f) d=%.1f du=%.1f bw=%s bh=%s' % (
        t.get('mx', 0), t.get('my', 0), t.get('cx', 0), t.get('cy', 0), t.get('d', 0), t.get('du', 0), t.get('bw'), t.get('bh'),
        w.get('mx', 0), w.get('my', 0), w.get('cx', 0), w.get('cy', 0), w.get('d', 0), w.get('du', 0), w.get('bw'), w.get('bh')))
json.dump(out, open(f'/home/user/quantiphy-challenge/research/next/labaudit2/0031/track_{R}.json', 'w'), indent=0)
