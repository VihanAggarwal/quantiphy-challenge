"""Pencil bag in camera b: orange mask, principal axis, end points -> table-plane coordinates at the axis height."""
import sys, numpy as np, cv2
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0034/scripts')
from calib_b import fit, backproject
im = cv2.imread('/home/user/quantiphy-challenge/research/next/labaudit2/0034/img/bx_20.png')
hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(int)
m = ((hsv[..., 0] >= 8) & (hsv[..., 0] <= 30) & (hsv[..., 1] > 110) & (hsv[..., 2] > 120)).astype(np.uint8)
m[:300] = 0; m[400:] = 0; m[:, :630] = 0; m[:, 760:] = 0
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
n, lab, st, cen = cv2.connectedComponentsWithStats(m); k = np.argmax(st[1:, 4]) + 1
ys, xs = np.nonzero(lab == k); P = np.c_[xs, ys].astype(float); mu = P.mean(0)
u, s, vt = np.linalg.svd(P - mu); ax = vt[0]; pr = (P - mu) @ ax; perp = (P - mu) @ vt[1]
e1 = mu + ax * pr.min(); e2 = mu + ax * pr.max()
print('bag mask area', st[k][4], 'ends px', e1.round(1), e2.round(1), 'len px %.1f width px %.1f' % (pr.ptp() if hasattr(pr,'ptp') else np.ptp(pr), np.ptp(perp)))
for f in (692, 711):
    cam = fit(f=f)
    for h in (0.0, 3.0, 3.5, 4.0):
        Q, _ = backproject(cam, [e1, e2], h)
        print(f'f={f} plane h={h}: length {np.linalg.norm(Q[1]-Q[0]):.1f} cm  ends {Q[0][:2].round(1)} {Q[1][:2].round(1)}')
cv2.imwrite('/home/user/quantiphy-challenge/research/next/labaudit2/0034/img/bag_mask_b.png', cv2.resize(((lab == k) * 255).astype(np.uint8)[280:420, 600:800], None, fx=3, fy=3))
