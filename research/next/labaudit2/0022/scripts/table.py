"""Table-top plane from the x render: edge lines fitted to the mask boundary / top-to-front-face transition,
corners = line intersections (the real corners are rounded), PnP with 76.0 x 60.3 cm at f = 711 (and f 716),
both side assignments. Saves plane.json {n, d (m), corners}."""
import sys, json, cv2, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0022/scripts')
from common import *
fr = frames('x')
med = np.median(fr[::3], axis=0).astype(np.float32)
lum = med.mean(2)
mask = med.max(2) > 45
def fitline(pts):
    pts = np.array(pts, float)
    for _ in range(3):
        vx, vy, x0, y0 = cv2.fitLine(pts.astype(np.float32), cv2.DIST_L2, 0, 0.01, 0.01).ravel()
        nrm = np.array([-vy, vx]); res = (pts - [x0, y0]) @ nrm
        keep = np.abs(res) < max(1.0, 2.5 * np.std(res)); pts = pts[keep]
    return np.array([x0, y0]), np.array([vx, vy]), np.std(res[keep]), len(pts)
def isect(L1, L2):
    (p, d), (q, e) = L1[:2], L2[:2]
    A = np.array([d, -e]).T; t = np.linalg.solve(A, q - p); return p + t[0] * d
# subpixel boundary along a scan: position where max-channel crosses midway between in/out levels
mx = med.max(2)
def cross(prof, lo_idx, hi_idx):
    a = prof.astype(float); lvl = 0.5 * (a[lo_idx] + a[hi_idx])
    s = np.sign(a - lvl); i = np.where(np.diff(s) != 0)[0]
    if len(i) == 0: return None
    i = i[0]; return i + (lvl - a[i]) / (a[i + 1] - a[i])
far = []; 
for u in range(305, 575, 2):
    col = mx[330:440, u]; c = cross(col, 0, -1)
    if c is not None: far.append([u, 330 + c])
left = []
for v in range(440, 590, 2):
    row = mx[v, 180:330]; c = cross(row, 0, -1)
    if c is not None: left.append([180 + c, v])
right = []
for v in range(380, 500, 2):
    row = mx[v, 560:720][::-1]; c = cross(row, 0, -1)
    if c is not None: right.append([719 - c, v])
# near edge: top surface (bright) -> front face (darker): strongest negative vertical gradient of luminance near the
# guessed line NL(224.7,613.9) - NR(671.1,513.5)
near = []
g = cv2.Sobel(cv2.GaussianBlur(lum, (3, 3), 0), cv2.CV_32F, 0, 1, ksize=3)
for u in range(250, 650, 2):
    vg = 613.9 + (u - 224.7) / (671.1 - 224.7) * (513.5 - 613.9)
    v0 = int(vg) - 8; seg = g[v0:v0 + 16, u]; i = int(np.argmin(seg))
    if 0 < i < 15:
        y1, y2, y3 = seg[i - 1:i + 2]; off = 0.5 * (y1 - y3) / (y1 - 2 * y2 + y3)
        near.append([u, v0 + i + off])
L = {k: fitline(p) for k, p in [('far', far), ('left', left), ('right', right), ('near', near)]}
for k, l in L.items(): print(k, 'pts', l[3], 'resid sd %.2f px' % l[2])
FL = isect(L['far'], L['left']); FR = isect(L['far'], L['right']); NR = isect(L['near'], L['right']); NL = isect(L['near'], L['left'])
C = np.array([FL, FR, NR, NL]); print('corners FL FR NR NL', np.round(C, 1).tolist())
out = {'corners': C.tolist()}
for f in (711.0, 716.0):
    K = np.array([[f, 0, CX], [0, f, CY], [0, 0, 1]])
    for name, (a, b) in {'far=76': (0.760, 0.603), 'far=60.3': (0.603, 0.760)}.items():
        obj = np.array([[0, 0, 0], [a, 0, 0], [a, b, 0], [0, b, 0]], float)
        ok, rv, tv = cv2.solvePnP(obj, C, K, None, flags=cv2.SOLVEPNP_IPPE)
        R, _ = cv2.Rodrigues(rv); proj, _ = cv2.projectPoints(obj, rv, tv, K, None)
        err = np.abs(proj.reshape(-1, 2) - C).max()
        n = R[:, 2]; d = float(n @ tv.ravel())
        if d < 0: n, d = -n, -d
        print(f'f {f} {name}: reproj max err {err:.2f} px, normal {np.round(n, 3)}, plane dist {d:.4f} m, '
              f'corner ranges {[round(float(np.linalg.norm(R @ o + tv.ravel())), 3) for o in obj]}')
        out[f'{f}_{name}'] = {'n': n.tolist(), 'd': d, 'err': float(err), 'R': R.tolist(), 't': tv.ravel().tolist()}
json.dump(out, open(f'{B}/plane.json', 'w'), indent=1)
vis = med.astype(np.uint8).copy()
for p in C: cv2.circle(vis, tuple(int(round(x)) for x in p), 4, (0, 0, 255), 1)
for pts, col in [(far, (0, 255, 0)), (left, (255, 0, 0)), (right, (255, 0, 255)), (near, (0, 255, 255))]:
    for p in pts: cv2.circle(vis, (int(p[0]), int(p[1])), 1, col, -1)
cv2.imwrite(f'{B}/img/table_fit.jpg', vis[330:640, 180:720])
