"""Table plane: back corners from edge fits on the x-render median top boundary, front corners read from zooms
(z_FL, z_FR). Plane via IPPE PnP with the stated table size 76.0 x 60.3 cm; also the vanishing-point check."""
import cv2, numpy as np, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0038/scripts')
from common import B, F, CX, CY
m = cv2.imread(f'{B}/median_x.png').astype(int)
mask = (m.sum(-1) > 40).astype(np.uint8); mask[600:] = 0
n, lab, st, cen = cv2.connectedComponentsWithStats(mask)
k = 1 + np.argmax(st[1:, 4]); mask = lab == k
top = {x: np.nonzero(mask[:, x])[0].min() for x in range(200, 1150) if mask[:, x].any()}
def fit(xs):
    xs = np.array([x for x in xs if x in top]); ys = np.array([top[x] for x in xs], float)
    p = np.polyfit(xs, ys, 1)
    for _ in range(4):
        keep = np.abs(ys - np.polyval(p, xs)) < 1.5; p = np.polyfit(xs[keep], ys[keep], 1)
    return p
L = fit(range(230, 435)); Bk = fit(list(range(470, 630)) + list(range(800, 905))); R = fit(range(935, 1125))
def inter(p, q):
    x = (q[1] - p[1]) / (p[0] - q[0]); return np.array([x, np.polyval(p, x)])
BL, BR = inter(L, Bk), inter(Bk, R)
FL, FR = np.array([210.0, 538.0]), np.array([1138.5, 587.5])
print('BL', BL.round(1), 'BR', BR.round(1), 'FL', FL, 'FR', FR)
img = np.array([FL, FR, BR, BL])
K = np.array([[F, 0, CX], [0, F, CY], [0, 0, 1.]])
obj = np.array([[0, 0, 0], [.760, 0, 0], [.760, .603, 0], [0, .603, 0]], float)
ok, rv, t = cv2.solvePnP(obj, img, K, None, flags=cv2.SOLVEPNP_IPPE)
Rm = cv2.Rodrigues(rv)[0]
proj, _ = cv2.projectPoints(obj, rv, t, K, None)
print('reproj err px', np.abs(proj.reshape(-1, 2) - img).max().round(2))
nrm = Rm[:, 2]; d = float(nrm @ t.ravel())
if d < 0: nrm, d = -nrm, -d
print('plane normal', nrm.round(4), 'camera height above table (m)', round(d, 4))
# orthogonality of the vanishing directions at f
Hn = cv2.getPerspectiveTransform(np.float32([[0,0],[1,0],[1,1],[0,1]]), np.float32(img))
M = np.linalg.inv(K) @ Hn; h1, h2 = M[:, 0], M[:, 1]
print('cos between table axes at f=711:', round(h1 @ h2 / np.linalg.norm(h1) / np.linalg.norm(h2), 4),
      ' aspect (|h1|/|h2| vs 76/60.3=1.260):', round(np.linalg.norm(h1) / np.linalg.norm(h2), 3))
np.save(f'{B}/plane.npy', np.r_[nrm, d]); np.save(f'{B}/pose.npy', np.r_[rv.ravel(), t.ravel()])
