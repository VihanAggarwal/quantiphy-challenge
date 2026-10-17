import cv2, numpy as np, sys
v = sys.argv[1] if len(sys.argv) > 1 else 'captured_0014'
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4' % v)
fr = []
while True:
    ok, f = c.read()
    if not ok: break
    fr.append(f.astype(np.float32))
bg = np.median(np.stack(fr[30:49]), axis=0)
res = []
for i in range(0, 27):
    d = np.abs(fr[i] - bg).sum(2)
    roi = np.zeros_like(d); roi[260:520, 470:640] = 1
    d = d * roi
    m = (d > 40).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n > 1:
        k = 1 + np.argmax(st[1:, 4])
        x, y, w, h, a = st[k]
        print(i, 'bbox x %d-%d y %d-%d w %d h %d area %d cen %.1f %.1f' % (x, x + w - 1, y, y + h - 1, w, h, a, cen[k][0], cen[k][1]))
