import cv2, sys
v = sys.argv[1]; idx = [int(i) for i in sys.argv[2].split(',')]
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_%s.mp4' % v)
i = 0
while True:
    ok, f = c.read()
    if not ok: break
    if i in idx: cv2.imwrite('g_%s_%02d.png' % (v, i), f)
    i += 1
