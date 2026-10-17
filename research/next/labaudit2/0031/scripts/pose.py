"""Camera pose from table-top corners (PnP), f variants, both orientations of the 76.0 x 60.3 top.
Prints reprojection error, camera height above the table top, and plane (n, d) in camera coords.
"""
import cv2, numpy as np, json
C = json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0031/corners.json'))
img = np.array([C['FL'], C['FR'], C['BR'], C['BL']], float)
res = {}
for f in (650, 680, 711, 740, 760):
    K = np.array([[f, 0, 640], [0, f, 360], [0, 0, 1.]])
    for W, Lg in ((60.3, 76.0), (76.0, 60.3)):
        obj = np.array([[0, 0, 0], [W, 0, 0], [W, Lg, 0], [0, Lg, 0]], float)  # x right, y away (back), z up
        ok, rv, tv = cv2.solvePnP(obj, img, K, None, flags=cv2.SOLVEPNP_IPPE)
        ok, rv, tv = cv2.solvePnP(obj, img, K, None, rv, tv, useExtrinsicGuess=True, flags=cv2.SOLVEPNP_ITERATIVE)
        Rm, _ = cv2.Rodrigues(rv)
        pr, _ = cv2.projectPoints(obj, rv, tv, K, None)
        err = np.sqrt(((pr.reshape(-1, 2) - img) ** 2).sum(1)).mean()
        cam = -Rm.T @ tv.ravel()     # camera centre in table coords
        n_cam = Rm @ np.array([0, 0, 1.])   # table normal (up) in camera coords
        d_cam = n_cam @ tv.ravel()   # plane: n.X = d  (X camera coords, cm)
        print('f=%d W=%.1f L=%.1f err=%.2fpx  cam(table)=(%.1f, %.1f, %.1f)cm  n_cam=%s d=%.2f' % (
            f, W, Lg, err, *cam, n_cam.round(4), d_cam))
        res[f'{f}_{W}'] = dict(f=f, W=W, L=Lg, err=err, cam=cam.tolist(), R=Rm.tolist(), t=tv.ravel().tolist())
json.dump(res, open('/home/user/quantiphy-challenge/research/next/labaudit2/0031/pose.json', 'w'))

# homography-only check: rectified aspect from vanishing points for a given f
def vp(p1, p2, p3, p4):
    l1 = np.cross([*p1, 1], [*p2, 1]); l2 = np.cross([*p3, 1], [*p4, 1]); v = np.cross(l1, l2); return v
v_depth = vp(C['FL'], C['BL'], C['FR'], C['BR'])
v_width = vp(C['FL'], C['FR'], C['BL'], C['BR'])
print('VP depth', (v_depth[:2] / v_depth[2]).round(1), 'VP width (homog)', v_width.round(3))
# focal from orthogonality if both finite: (v1-p).(v2-p) + f^2 = 0
p = np.array([640, 360.])
a = v_depth[:2] / v_depth[2]
if abs(v_width[2]) > 1e-9:
    b = v_width[:2] / v_width[2]
    f2 = -((a - p) @ (b - p))
    print('f from VPs:', np.sqrt(f2) if f2 > 0 else 'n/a', 'VPw', b.round(1))
