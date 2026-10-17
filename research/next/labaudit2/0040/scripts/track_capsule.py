"""Ball centre per video frame: (a) visible-blob centroid, (b) capsule (motion-blurred disc) fitted to the
blob boundary pixels that border empty background (occlusion edges against static objects excluded).
Frames from round 1 (research/next/labaudit/0040/frames). Output track_caps_<R>.json."""
import cv2, numpy as np, json, sys

def least_squares(f, x0, f_scale=1.5, iters=60, **kw):
    """Robust (Cauchy-weighted) Gauss-Newton with numeric Jacobian (no scipy in this venv)."""
    x = np.array(x0, float)
    for _ in range(iters):
        r = f(x); w = 1.0 / (1.0 + (r / f_scale) ** 2)
        J = np.empty((len(r), len(x)))
        for j in range(len(x)):
            h = 1e-4 * max(1.0, abs(x[j])); xp = x.copy(); xp[j] += h
            J[:, j] = (f(xp) - r) / h
        Wj = J * w[:, None]
        dx = np.linalg.lstsq(Wj.T @ J + 1e-6 * np.eye(len(x)), -(Wj.T @ r), rcond=None)[0]
        x = x + dx
        if np.abs(dx).max() < 1e-4: break
    class S: pass
    s = S(); s.x = x; s.fun = f(x); return s
R = sys.argv[1] if len(sys.argv) > 1 else 'x'
base = '/home/user/quantiphy-challenge/research/next/labaudit/0040/frames'
OUT = '/home/user/quantiphy-challenge/research/next/labaudit2/0040'
fr = [cv2.imread(f'{base}/v{R}_{i:02d}.png') for i in range(49)]
A = np.stack(fr).astype(np.int16)
med = np.median(A, axis=0)
if R == 'x':
    bg = med.sum(-1) < 40                      # empty background in the static scene
else:                                           # green screen: background = green
    b, g, r = med[..., 0], med[..., 1], med[..., 2]
    bg = (g > r + 25) & (g > b + 25)
out = {}
def seg_dist(p, c, th, L):
    d = np.array([np.cos(th), np.sin(th)])
    q = p - c
    s = np.clip(q @ d, -L, L)
    return np.linalg.norm(q - s[:, None] * d, axis=1)
for i in range(22, 49):
    d = np.abs(A[i] - med).max(-1)
    gimg = cv2.cvtColor(fr[i], cv2.COLOR_BGR2GRAY)
    m = ((d > 35) & (gimg > 120)).astype(np.uint8)
    m[690:] = 0
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n <= 1: continue
    k = 1 + np.argmax(st[1:, 4]); M = lab == k
    ys, xs = np.nonzero(M)
    c0 = np.array([xs.mean(), ys.mean()])
    C = np.cov(np.vstack([xs, ys])); w, v = np.linalg.eigh(C)
    th0 = np.arctan2(v[1, 1], v[0, 1])
    # boundary pixels of M whose 4-neighbour outside M is empty background in this frame
    Mu = M.astype(np.uint8)
    er = cv2.erode(Mu, np.ones((3, 3), np.uint8))
    bd = (Mu - er).astype(bool)
    dil_bg = cv2.dilate((bg & ~M).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    obj_near = cv2.dilate((~bg & ~M).astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
    good = bd & dil_bg & ~obj_near
    by, bx = np.nonzero(good)
    P = np.c_[bx, by].astype(float)
    frac = len(P) / max(1, bd.sum())
    res = dict(u=c0[0], v=c0[1], area=int(M.sum()), n_edge=int(len(P)), edge_frac=round(frac, 3))
    if len(P) > 30:
        def f(x):
            return seg_dist(P, x[:2], x[2], abs(x[3])) - x[4]
        x0 = [c0[0], c0[1], th0, 2 * np.sqrt(w[1]) - 2 * np.sqrt(w[0]), 2 * np.sqrt(w[0])]
        sol = least_squares(f, x0, loss='soft_l1', f_scale=1.5)
        cx, cy, th, L, r = sol.x
        res.update(cu=cx, cv=cy, th=float(np.degrees(th) % 180), L=abs(L), r=r, rms=float(np.sqrt(np.mean(sol.fun ** 2))))
        # fixed-radius variant (r = 20 px class) for robustness
        out[i] = res
    else:
        out[i] = res
    e = out[i]
    s = f"{i:2d} cen=({e['u']:6.1f},{e['v']:6.1f}) area={e['area']:5d} edge={e['n_edge']:4d} ({e['edge_frac']:.2f})"
    if 'cu' in e:
        s += f"  caps=({e['cu']:6.1f},{e['cv']:6.1f}) th={e['th']:5.1f} L={e['L']:5.1f} r={e['r']:5.1f} rms={e['rms']:.2f}  dcen=({e['cu']-e['u']:+5.1f},{e['cv']-e['v']:+5.1f})"
    print(s)
json.dump(out, open(f'{OUT}/track_caps_{R}.json', 'w'), indent=1)
