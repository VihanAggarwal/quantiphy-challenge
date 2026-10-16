"""Recover table plane from 4 corners + K, for both side assignments; report consistency."""
import cv2, numpy as np
F, CX, CY = 711.0, 640.0, 360.0
K = np.array([[F, 0, CX], [0, F, CY], [0, 0, 1.]])
img = np.array([[210, 538], [1138, 587], [917.8, 467.1], [448.5, 448.8]], float)  # FL FR BR BL
def pose(W, D):
    obj = np.array([[0, 0, 0], [W, 0, 0], [W, D, 0], [0, D, 0]], float)
    ok, rv, t = cv2.solvePnP(obj, img, K, None, flags=cv2.SOLVEPNP_IPPE)
    Rm = cv2.Rodrigues(rv)[0]
    proj, _ = cv2.projectPoints(obj, rv, t, K, None)
    err = np.abs(proj.reshape(-1, 2) - img).max()
    return Rm, t.ravel(), err
for W, D in [(76.0, 60.3), (60.3, 76.0)]:
    Rm, t, err = pose(W / 100, D / 100)
    n = Rm[:, 2]; d = n @ t
    print(f'W={W} D={D} reproj max err {err:.2f}px  normal {n.round(3)} offset {d:.3f}')
# homography-based aspect estimate with known f: rectify and compute ratio
Hn = cv2.getPerspectiveTransform(np.float32([[0,0],[1,0],[1,1],[0,1]]), np.float32(img))
Kinv = np.linalg.inv(K)
M = Kinv @ Hn
h1, h2 = M[:, 0], M[:, 1]
print('aspect |h1|/|h2| (front edge / side edge) =', np.linalg.norm(h1) / np.linalg.norm(h2), ' orthogonality cos', h1 @ h2 / np.linalg.norm(h1) / np.linalg.norm(h2))
for fx in (680, 700, 711, 720, 740):
    Kf = np.array([[fx, 0, CX], [0, fx, CY], [0, 0, 1.]]); M = np.linalg.inv(Kf) @ Hn
    h1, h2 = M[:, 0], M[:, 1]
    print(fx, 'aspect', round(np.linalg.norm(h1) / np.linalg.norm(h2), 4), 'cos', round(h1 @ h2 / np.linalg.norm(h1) / np.linalg.norm(h2), 4))

print('--- table-plane ranges at object pixels (W=76 along front edge) ---')
Rm, t, err = pose(0.76, 0.603)
n = Rm[:, 2]; d = n @ t
def onplane(u, v, h=0.0):
    r = np.array([(u - CX) / F, (v - CY) / F, 1.0]); r /= np.linalg.norm(r)
    s = (d + h * (-1 if n[1] < 0 else 1) * 0) / (n @ r)
    return s * r
for name, u, v, stated in [('credit card centre', 563, 540, 0.69), ('poker tower base', 685, 495, 0.91),
                           ('tape base', 590, 482, 0.973), ('cup base centre', 776, 500, 0.842),
                           ('jar base', 511, 494, None), ('FL', 210, 538, None), ('FR', 1138, 587, None),
                           ('BR', 917.8, 467.1, None), ('BL', 448.5, 448.8, None)]:
    X = onplane(u, v)
    print(f'{name:20s} ({u},{v}) range {np.linalg.norm(X):.3f}  Z {X[2]:.3f} stated {stated}')
