import cv2, numpy as np
r = np.load('t59b.npy')
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0059.mp4')
F = {}
i = 0
while True:
    ok, im = c.read()
    if not ok: break
    F[i] = im; i += 1
tiles = []
for fr in (70, 75, 86, 90):
    row = r[r[:, 0] == fr][0]
    x, y = int(row[1]), int(row[2])
    cr = F[fr][max(0,y-100):y+100, x-100:x+100].copy()
    cr = cv2.resize(cr, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    # gridlines every 20 px original
    for k in range(0, 400, 40):
        cv2.line(cr, (k, 0), (k, 5), (0, 255, 0), 1); cv2.line(cr, (0, k), (5, k), (0, 255, 0), 1)
    cv2.putText(cr, str(fr), (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    # enhance contrast
    cr = cv2.convertScaleAbs(cr, alpha=1.8, beta=-60)
    tiles.append(cr)
h = min(t.shape[0] for t in tiles)
cv2.imwrite('/home/user/quantiphy-challenge/research/next/audit3/internet_03/c59ball.png', np.hstack([t[:h] for t in tiles]))
