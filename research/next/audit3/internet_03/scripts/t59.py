import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0059.mp4')
frames = []
i = 0
ref = None
res = []
while True:
    ok, im = c.read()
    if not ok: break
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
    # poster region for shake
    roi = g[200:720, 380:1460]
    if i == 78: pass
    frames.append((i, im))
    i += 1
# reference frame 78
gref = cv2.cvtColor(frames[78][1], cv2.COLOR_BGR2GRAY).astype(np.float32)[200:720, 380:1460]
win = cv2.createHanningWindow(gref.shape[::-1], cv2.CV_32F)
for i, im in frames:
    if i < 58: continue
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)[200:720, 380:1460]
    (dx, dy), r = cv2.phaseCorrelate(gref, g, win)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    b, gg, rr = [im[..., k].astype(int) for k in range(3)]
    mask = ((rr - b) > 25) & ((rr - gg) > 15) & (hsv[..., 2] > 30)
    mask = mask.astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(mask)
    if n <= 1:
        print(i, 'none', round(dx, 1), round(dy, 1)); continue
    k = 1 + np.argmax(st[1:, 4])
    x, y, w, h, a = st[k]
    ys, xs = np.nonzero(lab == k)
    # equivalent diameter
    d_eq = 2 * np.sqrt(a / np.pi)
    res.append((i, cen[k][0], cen[k][1], w, h, a, d_eq, dx, dy))
    print(i, 'c=(%.1f,%.1f) bbox w=%d h=%d area=%d deq=%.1f shift=(%.1f,%.1f) edge=%s' % (cen[k][0], cen[k][1], w, h, a, d_eq, dx, dy, x <= 0 or x + w >= 1919 or y <= 0 or y + h >= 1079))
np.save('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/s/t59.npy', np.array(res))
