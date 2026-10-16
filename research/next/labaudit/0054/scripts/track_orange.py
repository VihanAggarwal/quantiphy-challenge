"""Track the orange basketball in 0054ax (green bg) and 0054bx (black bg) by colour; report centre and size."""
import cv2, numpy as np, sys
D = '/home/user/quantiphy-challenge/research/next/labaudit/0054/frames/'
def orange_mask(im):
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    m = ((h >= 2) & (h <= 22) & (s > 90) & (v > 60)).astype(np.uint8)
    return m
def blob(m, near=None):
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
    if n <= 1: return None
    idx = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    ys, xs = np.nonzero(lab == idx)
    # fill holes
    mm = (lab == idx).astype(np.uint8)
    cnts, _ = cv2.findContours(mm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cnts, key=cv2.contourArea)
    area = cv2.contourArea(c)
    (cx, cy), r = cv2.minEnclosingCircle(c)
    x, y, w, h = cv2.boundingRect(c)
    return dict(cx=xs.mean(), cy=ys.mean(), area=area, deq=2*np.sqrt(area/np.pi), w=w, h=h, rmin=2*r, bx=x, by=y)
for v in sys.argv[1:]:
    print('render', v)
    for i in range(49):
        im = cv2.imread(D + '%s_%02d.png' % (v, i))
        m = orange_mask(im)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        b = blob(m)
        if b is None: print(i, None); continue
        print('%2d t=%.3f c=(%.1f,%.1f) deq=%.1f w=%d h=%d encl=%.1f' % (i, i/24, b['cx'], b['cy'], b['deq'], b['w'], b['h'], b['rmin']))
