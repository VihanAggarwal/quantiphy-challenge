import cv2, sys
# usage: grab.py video frame out [x0 y0 x1 y1] [scale]
v, fi, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4' % v)
c.set(cv2.CAP_PROP_POS_FRAMES, fi)
ok, f = c.read()
if len(sys.argv) > 7:
    x0, y0, x1, y1 = map(int, sys.argv[4:8]); f = f[y0:y1, x0:x1]
sc = float(sys.argv[8]) if len(sys.argv) > 8 else (float(sys.argv[4]) if len(sys.argv) == 5 else 1.0)
if sc != 1.0: f = cv2.resize(f, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA if sc < 1 else cv2.INTER_NEAREST)
cv2.imwrite('/home/user/quantiphy-challenge/research/next/audit3/sim2_20/png/' + out, f)
