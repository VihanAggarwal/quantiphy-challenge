import cv2, numpy as np, json, sys
C = json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0040/remeasure_b/table_corners.json'))
img = np.array([C['fl'], C['fr'], C['br'], C['bl']], np.float64)
res = {}
for f in [700, 711, 722, 740]:
    K = np.array([[f, 0, 640], [0, f, 360], [0, 0, 1.]])
    for Wd, Dp in [(76.0, 60.3), (60.3, 76.0)]:
        obj = np.array([[0, 0, 0], [Wd, 0, 0], [Wd, Dp, 0], [0, Dp, 0]], np.float64)
        ok, rv, tv = cv2.solvePnP(obj, img, K, None, flags=cv2.SOLVEPNP_IPPE)
        pr, _ = cv2.projectPoints(obj, rv, tv, K, None)
        err = np.sqrt(((pr.reshape(-1, 2) - img) ** 2).sum(1))
        R, _ = cv2.Rodrigues(rv)
        n = R[:, 2]  # table normal in camera coords (z of table frame)
        # camera position in table frame
        cam = -R.T @ tv.ravel()
        print('f %d W %.1f D %.1f  reproj %s  cam_in_table %s normal_cam %s' % (f, Wd, Dp, err.round(2), cam.round(1), n.round(3)))
        res['%d_%g' % (f, Wd)] = dict(R=R.tolist(), t=tv.ravel().tolist(), err=err.tolist())
json.dump(res, open('/home/user/quantiphy-challenge/research/next/labaudit2/0040/remeasure_b/pnp.json', 'w'))
