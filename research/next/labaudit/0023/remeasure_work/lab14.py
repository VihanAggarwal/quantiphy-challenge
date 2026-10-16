import cv2, numpy as np
BL, BR, FR, FL = np.load('t14_corners.npy')
src = np.array([BL, BR, FR, FL], np.float64)
obj = np.array([[0, 0, 0], [60.3, 0, 0], [60.3, 76, 0], [0, 76, 0]], np.float64)
K = np.array([[711, 0, 640], [0, 711, 360], [0, 0, 1.]])
ok, rv, tv = cv2.solvePnP(obj, src, K, None, flags=cv2.SOLVEPNP_IPPE)
R = cv2.Rodrigues(rv)[0]; n = R @ np.array([0, 0, 1.]); d = n @ tv.ravel()
Ki = np.linalg.inv(K)
def rng(p, hgt):
    r = Ki @ np.r_[p, 1.0]; dd = d - np.sign(d) * hgt
    return np.linalg.norm(r * dd / (n @ r))
for name, p, hgt, lab in [('pen', (470, 437), 0.6, 167.25), ('slope near (bottom edge)', (555, 419), 0.3, 170.10),
                          ('book top centre', (652, 410), 1.46, 166.5), ('table front-mid', (577, 478), 0, None)]:
    m = rng(p, hgt); print('%-26s model %.1f cm  label %s  ratio %s' % (name, m, lab, None if lab is None else round(lab / m, 3)))
