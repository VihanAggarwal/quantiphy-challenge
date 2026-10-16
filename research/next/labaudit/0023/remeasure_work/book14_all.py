import cv2, numpy as np
from quadfit import quad_from_mask
BL, BR, FR, FL = np.load('t14_corners.npy')
W_T, D_T = 60.3, 76.0
src = np.array([BL, BR, FR, FL], np.float64)
obj = np.array([[0, 0, 0], [W_T, 0, 0], [W_T, D_T, 0], [0, D_T, 0]], np.float64)
def analyse(q, f=711., cx=640., cy=360., t=1.46, rng=166.5):
    K = np.array([[f, 0, cx], [0, f, cy], [0, 0, 1.]])
    ok, rv, tv = cv2.solvePnP(obj, src, K, None, flags=cv2.SOLVEPNP_IPPE)
    R = cv2.Rodrigues(rv)[0]
    n_cam = R @ np.array([0, 0, 1.0])          # table normal in camera coords
    d_tab = (n_cam @ tv.ravel())                # plane: n.X = d_tab  (cm)
    Ki = np.linalg.inv(K); ray = lambda p: Ki @ np.r_[p, 1.0]
    # (a) table scale: top face plane offset by t toward the camera
    cam_side = -np.sign(d_tab)                  # camera at origin; moving toward camera reduces |d|
    d_top = d_tab + cam_side * t
    P = lambda p, d: ray(p) * d / (n_cam @ ray(p))
    C = np.array([P(p, d_top) for p in q])
    s = [np.linalg.norm(C[i] - C[(i + 1) % 4]) for i in range(4)]
    # (b) depth-label scale: rescale so the top-face centre is at range rng
    ctr = P(q.mean(0), d_top); k = rng / np.linalg.norm(ctr)
    return np.array(s), k, np.linalg.norm(ctr)
rows = []
for name in ['g_0014_00', 'g_0014_24', 'g_0014_48', 'g_0014s_00', 'g_0014s_24', 'g_0014s_48', 'g_0014x_00', 'g_0014x_24', 'g_0014x_48']:
    img = cv2.imread(name + '.png').astype(float)
    x0, y0, x1, y1 = 610, 370, 700, 450
    roi = img[y0:y1, x0:x1]; B, G, R = roi[..., 0], roi[..., 1], roi[..., 2]
    for th in [-5, 0, 5]:
        soft = np.clip(((B - R) - th) / 20 + 0.5, 0, 1) * (B > 140)
        q = quad_from_mask(soft, x0, y0)
        # order corners: TL, TR, BR, BL by angle around centre
        c = q.mean(0); ang = np.arctan2(q[:, 1] - c[1], q[:, 0] - c[0]); q = q[np.argsort(ang)]
        # after argsort by angle (-pi..pi, image y down): order is TL?, TR?, BR?, BL? -> verify by positions
        s, k, rc = analyse(q)
        shorts = sorted(s)[:2]; longs = sorted(s)[2:]
        rows.append((name, th, np.mean(shorts), np.mean(longs), k))
        print('%-11s th%+d  sides %s  W(table)=%.2f L(table)=%.2f | range(table model) %.1f cm -> depth scale x%.3f: W=%.2f L=%.2f' % (
            name, th, np.round(s, 2), np.mean(shorts), np.mean(longs), rc, k, k * np.mean(shorts), k * np.mean(longs)))
r = np.array([(a[2], a[3], a[4]) for a in rows])
print('MEAN table-scale W %.2f L %.2f | depth-scale W %.2f L %.2f | W/L %.3f' % (r[:, 0].mean(), r[:, 1].mean(), (r[:, 0] * r[:, 2]).mean(), (r[:, 1] * r[:, 2]).mean(), (r[:, 0] / r[:, 1]).mean()))
print('spread W(table) min %.2f max %.2f' % (r[:, 0].min(), r[:, 0].max()))
