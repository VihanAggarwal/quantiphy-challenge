import cv2, sys
# usage: frame.py video frame out [x0 y0 x1 y1] [scale]
v, f, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4' % v)
c.set(cv2.CAP_PROP_POS_FRAMES, f)
ok, im = c.read()
if len(sys.argv) > 7:
    x0, y0, x1, y1 = map(int, sys.argv[4:8]); im = im[y0:y1, x0:x1]
sc = float(sys.argv[8]) if len(sys.argv) > 8 else 1.0
if sc != 1.0: im = cv2.resize(im, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA if sc < 1 else cv2.INTER_NEAREST)
cv2.imwrite(out, im)
print(im.shape)
