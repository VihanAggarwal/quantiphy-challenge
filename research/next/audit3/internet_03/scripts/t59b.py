import cv2, numpy as np
r = np.load('t59.npy')
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0059.mp4')
F = []
while True:
    ok, im = c.read()
    if not ok: break
    F.append(im)
gref = cv2.cvtColor(F[78], cv2.COLOR_BGR2GRAY).astype(np.float32)[200:720, 380:1460]
win = cv2.createHanningWindow(gref.shape[::-1], cv2.CV_32F)
def shift(i):
    g = cv2.cvtColor(F[i], cv2.COLOR_BGR2GRAY).astype(np.float32)[200:720, 380:1460]
    return cv2.phaseCorrelate(gref, g, win)[0]
# background: frame 60 (no ball)
bgi = 60
sb = shift(bgi)
out = []
for row in r:
    i = int(row[0])
    if i < 65 or i > 98: continue
    s = shift(i)
    M = np.float32([[1, 0, s[0] - sb[0]], [0, 1, s[1] - sb[1]]])
    bg = cv2.warpAffine(F[bgi], M, (1920, 1080), borderMode=cv2.BORDER_REPLICATE)
    d = np.abs(F[i].astype(int) - bg.astype(int)).sum(2)
    x0, y0 = int(row[1]), int(row[2])
    sub = np.zeros_like(d); 
    ys, xs = slice(max(0, y0 - 110), y0 + 110), slice(max(0, x0 - 110), x0 + 110)
    sub[ys, xs] = d[ys, xs]
    m = (sub > 45).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    k = 1 + np.argmax(st[1:, 4])
    yy, xx = np.nonzero(lab == k)
    out.append((i, cen[k][0], cen[k][1], yy, xx, s))
# velocity direction
cx = np.array([o[1] for o in out]); cy = np.array([o[2] for o in out]); ii = np.array([o[0] for o in out])
res = []
for j, (i, x, y, yy, xx, s) in enumerate(out):
    j0, j1 = max(0, j - 1), min(len(out) - 1, j + 1)
    v = np.array([cx[j1] - cx[j0], cy[j1] - cy[j0]]); v /= np.linalg.norm(v)
    p = np.array([-v[1], v[0]])
    proj = (xx - x) * p[0] + (yy - y) * p[1]
    projv = (xx - x) * v[0] + (yy - y) * v[1]
    dperp = proj.max() - proj.min() + 1
    dpar = projv.max() - projv.min() + 1
    clipped = yy.min() <= 0 or xx.min() <= 0 or xx.max() >= 1919 or yy.max() >= 1079
    res.append((i, x, y, dperp, dpar, s[0], s[1], clipped))
    print(i, 'c=(%.1f,%.1f) dperp=%.0f dpar=%.0f area_eq=%.0f clipped=%s' % (x, y, dperp, dpar, 2*np.sqrt(len(xx)/np.pi), clipped))
np.save('t59b.npy', np.array(res, dtype=float))
