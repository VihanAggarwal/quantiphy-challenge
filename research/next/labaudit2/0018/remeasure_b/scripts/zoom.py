import cv2, numpy as np, sys
vid, i, x0, y0, x1, y1, s = sys.argv[1], int(sys.argv[2]), *map(int, sys.argv[3:8])
out = sys.argv[8]
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
c.set(cv2.CAP_PROP_POS_FRAMES, i)
ok, f = c.read()
cr = cv2.resize(f[y0:y1, x0:x1], None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC)
for x in range(x0 - x0 % 10, x1, 10):
    X = (x - x0) * s
    if X < 0: continue
    L = 14 if x % 50 == 0 else 6
    cv2.line(cr, (X, 0), (X, L), (0, 0, 255), 1)
    if x % 50 == 0: cv2.putText(cr, str(x), (X + 2, 26), 0, 0.4, (0, 0, 255), 1)
for y in range(y0 - y0 % 10, y1, 10):
    Y = (y - y0) * s
    if Y < 0: continue
    L = 14 if y % 50 == 0 else 6
    cv2.line(cr, (0, Y), (L, Y), (0, 0, 255), 1)
    if y % 50 == 0: cv2.putText(cr, str(y), (16, Y + 4), 0, 0.4, (0, 0, 255), 1)
cv2.imwrite(out, cr)
