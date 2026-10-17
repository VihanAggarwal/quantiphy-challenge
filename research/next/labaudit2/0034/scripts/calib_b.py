"""Camera b: table-top homography from the 4 top-surface corners (76.0 x 60.3 cm), f from the homography
(principal point at image centre), pose, and back-projection of image points onto a plane at height h above the top."""
import numpy as np, cv2, json
CORN = np.array([[497, 243], [804, 250], [853, 427], [433, 413]], float)   # TL, TR, BR, BL (top surface)
W = np.array([[0, 0], [76.0, 0], [76.0, 60.3], [0, 60.3]], float)
c = np.array([640.0, 360.0])

def fit(corn=CORN, f=None):
    H, _ = cv2.findHomography(W, corn)
    Hn = H.copy(); Hn[0] -= c[0] * Hn[2]; Hn[1] -= c[1] * Hn[2]   # remove principal point
    h1, h2 = Hn[:, 0], Hn[:, 1]
    if f is None:
        # orthogonality: h1x h2x/f^2 + h1y h2y/f^2 + h1z h2z = 0
        f2a = -(h1[0] * h2[0] + h1[1] * h2[1]) / (h1[2] * h2[2])
        # equal norms
        f2b = -((h1[0]**2 + h1[1]**2) - (h2[0]**2 + h2[1]**2)) / (h1[2]**2 - h2[2]**2)
        f = np.sqrt(f2a) if f2a > 0 else np.nan
        fb = np.sqrt(f2b) if f2b > 0 else np.nan
    else:
        fb = f
    K = np.array([[f, 0, c[0]], [0, f, c[1]], [0, 0, 1]])
    ok, rv, tv = cv2.solvePnP(np.c_[W, np.zeros(4)], corn, K, None, flags=cv2.SOLVEPNP_IPPE)
    R, _ = cv2.Rodrigues(rv)
    return dict(f=f, fb=fb, K=K, R=R, t=tv.ravel())

def backproject(cam, uv, h):
    """image points -> world (X,Y,Z) on plane Z=-h (world Z axis: table normal; sign chosen so the camera has Z<0)."""
    K, R, t = cam['K'], cam['R'], cam['t']
    Cw = -R.T @ t                      # camera centre in world
    s = -1.0 if Cw[2] < 0 else 1.0     # height direction toward the camera
    out = []
    for u, v in np.atleast_2d(uv):
        d = R.T @ np.linalg.solve(K, [u, v, 1.0])
        lam = (s * h - Cw[2]) / d[2]
        out.append(Cw + lam * d)
    return np.array(out), Cw

if __name__ == '__main__':
    cam = fit()
    print('f (orth) %.1f  f (norm) %.1f' % (cam['f'], cam['fb']))
    _, Cw = backproject(cam, [[640, 360]], 0)
    print('camera centre (cm, table frame):', Cw.round(1), 'height above top', abs(Cw[2]).round(1))
    # reprojection check of the corners
    P, _ = cv2.projectPoints(np.c_[W, np.zeros(4)], cv2.Rodrigues(cam['R'])[0], cam['t'], cam['K'], None)
    print('corner reproj err px', np.abs(P.reshape(-1, 2) - CORN).max().round(2))
    for f in (cam['f'], 711, 760):
        cm = fit(f=f); _, C = backproject(cm, [[640, 360]], 0)
        print('f %.0f camera centre' % f, C.round(1))
