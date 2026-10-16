"""Fit table-top edges in the x-render median; recover plane via vanishing points and via homography (76.0 x 60.3)."""
import cv2, numpy as np
B = '/home/user/quantiphy-challenge/research/next/labaudit/0039'
F, CX, CY = 711.0, 640.0, 360.0
K = np.array([[F,0,CX],[0,F,CY],[0,0,1.]])
m = cv2.imread(f'{B}/median_0039x.png')
g = m.astype(int).sum(-1)
mask = (g > 60).astype(np.uint8); mask[690:] = 0
n_, lab, st, cen = cv2.connectedComponentsWithStats(mask)
k = 1 + np.argmax(st[1:, 4]); mask = (lab == k)
top = {x: np.nonzero(mask[:, x])[0].min() for x in range(209, 1142)}
# subpixel top boundary: use intensity crossing
gray = g/3.0
def subtop(x):
    y = top[x]
    col = gray[y-3:y+4, x]
    # threshold half between bg (~0) and table brightness
    hi = gray[y+4:y+8, x].mean(); thr = hi/2
    for j in range(len(col)-1):
        if col[j] < thr <= col[j+1]:
            return y-3+j + (thr-col[j])/(col[j+1]-col[j])
    return float(y)
def fit(xs):
    xs = np.array(list(xs)); ys = np.array([subtop(x) for x in xs], float)
    p = np.polyfit(xs, ys, 1)
    for _ in range(3):
        r = ys - np.polyval(p, xs); keep = np.abs(r) < 1.0
        p = np.polyfit(xs[keep], ys[keep], 1)
    return p, np.std((ys - np.polyval(p, xs))[keep])
L, sL = fit(range(235, 425))
Bk, sB = fit(list(range(455, 625)) + list(range(820, 905)))
R, sR = fit(range(940, 1125))
# front edge: transition from top surface (lighter) to front band (darker) in the o-median (x-median also has it)
mo = cv2.imread(f'{B}/median_0039x.png').astype(float).sum(-1)/3
fx, fy = [], []
for x in range(260, 1100, 4):
    y0 = int(537.5 + (588-537.5)*(x-211)/(1138-211))
    col = mo[y0-8:y0+9, x]
    d = np.diff(col)
    j = np.argmin(d)  # strongest light->dark drop going down
    fx.append(x); fy.append(y0-8+j+0.5)
fx = np.array(fx); fy = np.array(fy)
Fr = np.polyfit(fx, fy, 1)
for _ in range(3):
    r = fy-np.polyval(Fr, fx); keep = np.abs(r) < 1.5; Fr = np.polyfit(fx[keep], fy[keep], 1)
def inter(p, q):
    x = (q[1] - p[1]) / (p[0] - q[0]); return np.array([x, np.polyval(p, x)])
BL = inter(L, Bk); BR = inter(Bk, R); FL = inter(L, Fr); FR = inter(Fr, R)
print('fit sd', sL, sB, sR, 'front', Fr)
print('FL', FL, 'FR', FR, 'BR', BR, 'BL', BL)
def h(p): return np.array([p[0], p[1], 1.0])
# vanishing points
v1 = np.cross(np.cross(h(FL), h(FR)), np.cross(h(BL), h(BR)))  # left-right direction
v2 = np.cross(np.cross(h(FL), h(BL)), np.cross(h(FR), h(BR)))  # front-back direction
d1 = np.linalg.inv(K) @ v1; d1 /= np.linalg.norm(d1)
d2 = np.linalg.inv(K) @ v2; d2 /= np.linalg.norm(d2)
print('orthogonality cos', d1 @ d2)
n = np.cross(d1, d2); n /= np.linalg.norm(n)
if n[1] < 0: n = -n   # normal pointing down in camera coords (y down), i.e. from camera toward table: plane n.X = d
def ray(p): r = np.linalg.inv(K) @ h(p); return r
def onp(p, d): r = ray(p); return d / (n @ r) * r
# scale d from side lengths
for name, a, b, Lr in [('front', FL, FR, .760), ('back', BL, BR, .760), ('left', FL, BL, .603), ('right', FR, BR, .603)]:
    l1 = np.linalg.norm(onp(a, 1) - onp(b, 1)); print(name, 'h =', Lr/l1)
hs = [ .760/np.linalg.norm(onp(FL,1)-onp(FR,1)), .760/np.linalg.norm(onp(BL,1)-onp(BR,1)), .603/np.linalg.norm(onp(FL,1)-onp(BL,1)), .603/np.linalg.norm(onp(FR,1)-onp(BR,1))]
d = float(np.mean(hs))
print('n', n, 'camera height above table', d, 'tilt from normal deg', np.degrees(np.arccos(abs(n[1]))))
np.save(f'{B}/plane.npy', np.r_[n, d])
# Homography route (no vanishing-point step): solvePnP with the 4 corners
obj = np.array([[0,0,0],[.760,0,0],[.760,.603,0],[0,.603,0]], float)
img = np.array([FL, FR, BR, BL], float)
ok, rv, tv = cv2.solvePnP(obj, img, K, None, flags=cv2.SOLVEPNP_IPPE)
Rm, _ = cv2.Rodrigues(rv)
nz = Rm[:, 2]; dist = abs(nz @ tv.ravel())
print('PnP: normal', nz, 'height', dist)
proj, _ = cv2.projectPoints(obj, rv, tv, K, None); print('reproj err px', np.linalg.norm(proj.reshape(-1,2)-img, axis=1))
np.save(f'{B}/pose.npy', np.r_[rv.ravel(), tv.ravel()])
