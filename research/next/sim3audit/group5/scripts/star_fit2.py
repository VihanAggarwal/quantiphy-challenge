# simulation_0312: own silhouette fit of a rounded extruded 5-point star (independent implementation).
# Units: total star height H = 1. Thickness answer = 0.2 * T where T = Tc + 2b.
import sys, cv2, numpy as np, json
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/sim3audit/group5/scripts')
from lm import least_squares
F = float(sys.argv[1]) if len(sys.argv) > 1 else 1459.0
TH = np.deg2rad(float(sys.argv[2]) if len(sys.argv) > 2 else 18.4)
FRAMES = [int(x) for x in (sys.argv[3] if len(sys.argv) > 3 else '0,3,6,9,12,18,24,36,48,60,71').split(',')]
FIXT = float(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] not in ("", "none") else None
cap = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0312.mp4')
fr = []
while True:
    ok, f = cap.read()
    if not ok: break
    fr.append(f.astype(np.float32))
bg = np.array([155., 185., 197.])
C = 48; SS = 4; N = 2 * C
obs = {}; cen = {}
for k in FRAMES:
    d = (bg[0] - fr[k][..., 0]) + (bg[1] - fr[k][..., 1])
    m = d > 60
    ys, xs = np.where(m)
    cx, cy = int(round(xs.mean())), int(round(ys.mean()))
    crop = d[cy - C:cy + C, cx - C:cx + C]
    a = np.clip(crop / 150.0, 0, 1)
    # fill interior (highlights / light face) using hole filling of a low threshold mask, eroded
    mm = (crop > 40).astype(np.uint8)
    ff = mm.copy(); h, w = ff.shape; flood = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(ff, flood, (0, 0), 1)
    filled = mm | (1 - ff)
    inner = cv2.erode(filled, np.ones((5, 5), np.uint8))
    a[inner > 0] = 1.0
    obs[k] = a; cen[k] = (cx, cy)
up = np.array([0, -np.cos(TH), -np.sin(TH)]); hz = np.array([0, -np.sin(TH), np.cos(TH)]); rt = np.array([1., 0, 0])
_cache = {}
def star2d(q, Rc, c2=0.0):
    key = (round(q, 5), round(Rc, 5), round(c2, 5))
    if key in _cache: return _cache[key]
    ang = np.deg2rad(90 + 36 * np.arange(10)); r = np.where(np.arange(10) % 2 == 0, Rc, q * Rc)
    pts = np.stack([r * np.cos(ang), r * np.sin(ang)], 1)
    if c2 > 0:
        S = 600.0; off = 1.2
        img = np.zeros((int(2 * off * S), int(2 * off * S)), np.uint8)
        pp = np.stack([(pts[:, 0] + off) * S, (off - pts[:, 1]) * S], 1)
        cv2.fillPoly(img, [np.round(pp * 16).astype(np.int32)], 1, shift=4)
        dt = cv2.distanceTransform((1 - img).astype(np.uint8), cv2.DIST_L2, 5)
        img2 = (dt <= c2 * S).astype(np.uint8)
        cs, _ = cv2.findContours(img2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cc = max(cs, key=cv2.contourArea)[:, 0, :].astype(float)
        cc = cc[::3]
        pts = np.stack([cc[:, 0] / S - off, off - cc[:, 1] / S], 1)
    yc = 0.5 * (pts[:, 1].max() + pts[:, 1].min())
    pts = pts.copy(); pts[:, 1] -= yc
    _cache[key] = pts
    return pts
def render(k, g, pf):
    psi, q, b, Tc, sig, c2 = g
    Z, du, dv = pf
    Rc = (1 - 2 * b - 2 * c2) / (1 + np.cos(np.deg2rad(36)))
    P2 = star2d(q, Rc, c2)
    ex = np.cos(psi) * rt + np.sin(psi) * hz; ey = up; ez = -np.sin(psi) * rt + np.cos(psi) * hz
    cx, cy = cen[k]
    u0, v0 = cx + du, cy + dv
    ray = np.array([(u0 - 540) / F, (v0 - 540) / F, 1.0]); ray /= np.linalg.norm(ray)
    P = Z * ray
    canvas = np.zeros((N * SS, N * SS), np.uint8)
    for c in np.linspace(-Tc / 2, Tc / 2, 21):
        X = P[None] + P2[:, :1] * ex[None] + P2[:, 1:] * ey[None] + c * ez[None]
        u = 540 + F * X[:, 0] / X[:, 2]; v = 540 + F * X[:, 1] / X[:, 2]
        pts = np.stack([(u - (cx - C)) * SS, (v - (cy - C)) * SS], 1)
        cv2.fillPoly(canvas, [np.round(pts * 16).astype(np.int32)], 1, lineType=cv2.LINE_8, shift=4)
    bpx = b * F / Z * SS
    dt = cv2.distanceTransform((1 - canvas).astype(np.uint8), cv2.DIST_L2, 5)
    cov = (dt <= bpx).astype(np.float32)
    cov = cv2.resize(cov, (N, N), interpolation=cv2.INTER_AREA)
    cov = cv2.GaussianBlur(cov, (0, 0), max(sig, 0.3))
    return cov
def unpack(x):
    g = x[:6]; pf = x[6:].reshape(-1, 3); return g, pf
def resid(x):
    g, pf = unpack(x)
    if FIXT is not None:
        g = g.copy(); g[3] = max(FIXT - 2 * g[2], 0.0)
    return np.concatenate([(render(k, g, pf[i]) - obs[k]).ravel() for i, k in enumerate(FRAMES)])
# init Z from bbox height ~ H=1 -> Z = F * 1 / h_px
pf0 = []
for k in FRAMES:
    ys = np.where(obs[k].max(1) > 0.5)[0]; hpx = ys.max() - ys.min() + 1
    pf0 += [F / hpx, 0.0, 0.0]
best = None
for psi0 in [float(a) for a in (sys.argv[5] if len(sys.argv) > 5 else '116').split(',')]:
    psi0 = np.deg2rad(psi0)
    x0 = np.array([psi0, 0.55, 0.03, 0.10, 0.8, 0.05] + pf0)
    lo = np.array([-np.pi, 0.3, 0.0, 0.0, 0.3, 0.0] + [1, -15, -15] * len(FRAMES))
    hi = np.array([np.pi, 0.8, 0.2, 0.6, 3.0, 0.15] + [500, 15, 15] * len(FRAMES))
    st = np.array([np.deg2rad(1.0), 0.01, 0.004, 0.006, 0.05, 0.004] + [x * 0.01 for x in pf0[::3] for _ in [0]] * 0 + sum([[pf0[3*i] * 0.01, 0.25, 0.25] for i in range(len(FRAMES))], []))
    s = least_squares(resid, x0, lo, hi, iters=60, steps=st)
    print('start psi %.0f -> cost %.3f g=%s' % (np.rad2deg(psi0), s.cost, np.round(s.x[:6], 4)), flush=True)
    if best is None or s.cost < best.cost: best = s
g, pf = unpack(best.x)
psi, q, b, Tc, sig, c2 = g
if FIXT is not None: Tc = max(FIXT - 2 * b, 0)
Rc = (1 - 2 * b - 2 * c2) / (1 + np.cos(np.deg2rad(36)))
P2 = star2d(q, Rc, c2)
W = (P2[:, 0].max() - P2[:, 0].min()) + 2 * b
print('core 2D height check', P2[:, 1].max() - P2[:, 1].min() + 2 * b)
T = Tc + 2 * b
print('BEST cost %.3f c2=%.4f psi=%.1f deg q=%.3f b=%.4f Tc=%.4f sigma=%.2f  -> W/H=%.4f T/H=%.4f  thickness=%.4f m width=%.4f m' % (best.cost, c2, np.rad2deg(psi), q, b, Tc, sig, W, T, 0.2 * T, 0.2 * W))
print('per-frame Z (H units -> m = *0.2):', np.round(pf[:, 0] * 0.2, 3))
json.dump(dict(F=F, theta=float(np.rad2deg(TH)), frames=FRAMES, g=list(map(float, g)), pf=pf.tolist(), cost=float(best.cost), TH=float(T), WH=float(W)),
          open('/home/user/quantiphy-challenge/research/next/sim3audit/group5/star_fit2_%d_%s.json' % (int(F), 'free' if FIXT is None else 'T%.2f' % FIXT), 'w'))
