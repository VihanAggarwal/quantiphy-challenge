"""Fit table-top edges (left, back, right, front) in the x-render median, recover plane at f=711 (+ f check)."""
import cv2, numpy as np
B = '/home/user/quantiphy-challenge/research/next/labaudit/0038'
F, CX, CY = 711.0, 640.0, 360.0
m = cv2.imread(f'{B}/median_x.png')
g = m.astype(int).sum(-1)
mask = (g > 40).astype(np.uint8); mask[600:] = 0
n, lab, st, cen = cv2.connectedComponentsWithStats(mask)
k = 1 + np.argmax(st[1:, 4]); mask = (lab == k)
xs_all = np.nonzero(mask.any(0))[0]; print('x extent', xs_all.min(), xs_all.max())
top = {}
for x in range(xs_all.min(), xs_all.max()+1):
    ys = np.nonzero(mask[:, x])[0]
    top[x] = ys.min()
def fit(xs):
    xs = np.array([x for x in xs if x in top]); ys = np.array([top[x] for x in xs], float)
    p = np.polyfit(xs, ys, 1)
    for _ in range(3):
        r = ys - np.polyval(p, xs); keep = np.abs(r) < 1.5
        p = np.polyfit(xs[keep], ys[keep], 1)
    return p, keep.mean()
# print top profile coarse
for x in range(200, 1150, 25): print(x, top.get(x))
L, kl = fit(range(225, 440))
Bk, kb = fit(list(range(470, 625)) + list(range(805, 905)))
R, kr = fit(range(940, 1130))
print('inlier frac', kl, kb, kr)
def inter(p, q):
    x = (q[1] - p[1]) / (p[0] - q[0]); return np.array([x, np.polyval(p, x)])
BL = inter(L, Bk); BR = inter(Bk, R)
FL = np.array([210., 538.]); FR = np.array([1138., 588.])
print('BL', BL, 'BR', BR)
img = np.array([FL, FR, BR, BL])
K = np.array([[F, 0, CX], [0, F, CY], [0, 0, 1.]])
Hn = cv2.getPerspectiveTransform(np.float32([[0,0],[1,0],[1,1],[0,1]]), np.float32(img))
for fx in (680, 700, 711, 720, 740):
    Kf = np.array([[fx, 0, CX], [0, fx, CY], [0, 0, 1.]]); M = np.linalg.inv(Kf) @ Hn
    h1, h2 = M[:, 0], M[:, 1]
    print(fx, 'aspect', round(np.linalg.norm(h1) / np.linalg.norm(h2), 4), 'cos', round(h1 @ h2 / np.linalg.norm(h1) / np.linalg.norm(h2), 4))
obj = np.array([[0, 0, 0], [.76, 0, 0], [.76, .603, 0], [0, .603, 0]], float)
ok, rv, t = cv2.solvePnP(obj, img, K, None, flags=cv2.SOLVEPNP_IPPE)
Rm = cv2.Rodrigues(rv)[0]
proj, _ = cv2.projectPoints(obj, rv, t, K, None)
print('reproj err', np.abs(proj.reshape(-1, 2) - img).max())
nrm = Rm[:, 2]; d = nrm @ t.ravel()
if d < 0: nrm, d = -nrm, -d
print('plane normal', nrm.round(4), 'offset (cam height above table) m', round(d, 4))
np.save(f'{B}/plane.npy', np.r_[nrm, d])
np.save(f'{B}/pose.npy', np.r_[rv.ravel(), t.ravel()])
