import cv2, sys
v, f, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
scale = float(sys.argv[4]) if len(sys.argv)>4 else 0.5
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
c.set(cv2.CAP_PROP_POS_FRAMES, f)
ok, im = c.read()
if len(sys.argv)>5:
    x0,y0,x1,y1 = map(int, sys.argv[5].split(','))
    im = im[y0:y1, x0:x1]
im = cv2.resize(im, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
cv2.imwrite(out, im)
