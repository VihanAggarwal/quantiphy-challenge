"""Table plane from the four table-top corners in the x render (black background).
Top edges (left/back/right) from the mask boundary; front edge from the light->dark transition (top -> front band).
Two routes: vanishing points + known 76.0 x 60.3 sides, and solvePnP (IPPE) on the 4 corners."""
import cv2, numpy as np, sys, json
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0039/scripts')
from frames import load
OUT = '/home/user/quantiphy-challenge/research/next/labaudit2/0039'
F, CX, CY = 711.0, 640.0, 360.0
K = np.array([[F, 0, CX], [0, F, CY], [0, 0, 1.]])
fr = load('0039x')
med = np.median(fr[0:10], axis=0).astype(np.uint8)
cv2.imwrite(f'{OUT}/png/median_x.png', med)
g = med.astype(float).mean(-1)
mask = (g > 20).astype(np.uint8); mask[690:] = 0
n_, lab, st, cen = cv2.connectedComponentsWithStats(mask)
k = 1 + np.argmax(st[1:, 4]); mask = (lab == k)
def subtop(x):
    y = np.nonzero(mask[:, x])[0].min()
    col = g[y - 3:y + 4, x]; hi = g[y + 4:y + 8, x].mean(); thr = hi / 2
    for j in range(len(col) - 1):
        if col[j] < thr <= col[j + 1]:
            return y - 3 + j + (thr - col[j]) / (col[j + 1] - col[j])
    return float(y)
def rfit(xs, ys, tol):
    xs = np.array(xs, float); ys = np.array(ys, float); p = np.polyfit(xs, ys, 1)
    for _ in range(4):
        keep = np.abs(ys - np.polyval(p, xs)) < tol; p = np.polyfit(xs[keep], ys[keep], 1)
    return p, float(np.std((ys - np.polyval(p, xs))[keep])), int(keep.sum())
def edge(xr): xs = list(xr); return rfit(xs, [subtop(x) for x in xs], 1.0)
L = edge(range(235, 425)); Bk = edge(list(range(470, 620)) + list(range(820, 900))); R = edge(range(940, 1125))
fx, fy = [], []
for x in range(260, 1100, 4):
    y0 = int(537.5 + (588 - 537.5) * (x - 211) / (1138 - 211))
    col = g[y0 - 8:y0 + 9, x]; d = np.diff(col); j = np.argmin(d)
    fx.append(x); fy.append(y0 - 8 + j + 0.5)
Fr = rfit(fx, fy, 1.5)
print('edges (slope, icpt, sd, n):', 'L', L, 'B', Bk, 'R', R, 'F', Fr)
def inter(p, q): x = (q[1] - p[1]) / (p[0] - q[0]); return np.array([x, np.polyval(p, x)])
BL = inter(L[0], Bk[0]); BR = inter(Bk[0], R[0]); FL = inter(L[0], Fr[0]); FR = inter(Fr[0], R[0])
print('FL', FL, 'FR', FR, 'BR', BR, 'BL', BL)
h = lambda p: np.array([p[0], p[1], 1.0])
v1 = np.cross(np.cross(h(FL), h(FR)), np.cross(h(BL), h(BR)))
v2 = np.cross(np.cross(h(FL), h(BL)), np.cross(h(FR), h(BR)))
d1 = np.linalg.inv(K) @ v1; d1 /= np.linalg.norm(d1); d2 = np.linalg.inv(K) @ v2; d2 /= np.linalg.norm(d2)
print('VP orthogonality cos', d1 @ d2)
n = np.cross(d1, d2); n /= np.linalg.norm(n)
if n[1] < 0: n = -n
ray = lambda p: np.linalg.inv(K) @ h(p)
onp = lambda p, d: d / (n @ ray(p)) * ray(p)
hs = [.760 / np.linalg.norm(onp(FL, 1) - onp(FR, 1)), .760 / np.linalg.norm(onp(BL, 1) - onp(BR, 1)),
      .603 / np.linalg.norm(onp(FL, 1) - onp(BL, 1)), .603 / np.linalg.norm(onp(FR, 1) - onp(BR, 1))]
print('VP heights front/back/left/right', np.round(hs, 4), 'mean', np.mean(hs))
obj = np.array([[0, 0, 0], [.760, 0, 0], [.760, .603, 0], [0, .603, 0]], float)
img = np.array([FL, FR, BR, BL], float)
ok, rv, tv = cv2.solvePnP(obj, img, K, None, flags=cv2.SOLVEPNP_IPPE)
Rm, _ = cv2.Rodrigues(rv); nz = Rm[:, 2]; hp = abs(nz @ tv.ravel())
if nz[1] < 0: nz = -nz
proj, _ = cv2.projectPoints(obj, rv, tv, K, None)
print('PnP normal', nz, 'height', hp, 'reproj px', np.round(np.linalg.norm(proj.reshape(-1, 2) - img, axis=1), 2), 'angle between normals deg', np.degrees(np.arccos(min(1, abs(n @ nz)))))
json.dump(dict(n_vp=n.tolist(), h_vp=float(np.mean(hs)), h_vp_all=[float(x) for x in hs], n_pnp=nz.tolist(), h_pnp=float(hp),
               corners=dict(FL=FL.tolist(), FR=FR.tolist(), BR=BR.tolist(), BL=BL.tolist())), open(f'{OUT}/plane.json', 'w'), indent=1)
