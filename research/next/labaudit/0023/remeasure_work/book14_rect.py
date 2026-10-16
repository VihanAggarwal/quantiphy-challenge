import cv2, numpy as np
BL, BR, FR, FL = np.load('t14_corners.npy')
W_T, D_T = 60.3, 76.0
src = np.array([BL, BR, FR, FL], np.float32)
dst = np.array([[0, 0], [W_T, 0], [W_T, D_T], [0, D_T]], np.float32)
H = cv2.getPerspectiveTransform(src, dst)
import itertools
for th in ['book14_quad.npy']:
    q = np.load(th)
    p = cv2.perspectiveTransform(q.reshape(-1, 1, 2).astype(np.float32), H).reshape(-1, 2)
    s = [np.linalg.norm(p[i] - p[(i + 1) % 4]) for i in range(4)]
    print('rectified book corners', np.round(p, 2).tolist())
    print('sides', np.round(s, 2))
    # angle at corners
    for i in range(4):
        a = p[i - 1] - p[i]; b = p[(i + 1) % 4] - p[i]
        print(' angle', round(np.degrees(np.arccos(a @ b / np.linalg.norm(a) / np.linalg.norm(b))), 1))
# camera pose with f=711 for height correction
K = np.array([[711, 0, 640], [0, 711, 360], [0, 0, 1.]])
obj = np.array([[0, 0, 0], [W_T, 0, 0], [W_T, D_T, 0], [0, D_T, 0]], np.float64)
ok, rv, tv = cv2.solvePnP(obj, src.astype(np.float64), K, None, flags=cv2.SOLVEPNP_IPPE)
Rm = cv2.Rodrigues(rv)[0]
cam = -Rm.T @ tv
print('camera pos in table coords (cm)', cam.ravel())
rep = cv2.projectPoints(obj, rv, tv, K, None)[0].reshape(-1, 2)
print('reproj err', np.round(rep - src, 2).tolist())
