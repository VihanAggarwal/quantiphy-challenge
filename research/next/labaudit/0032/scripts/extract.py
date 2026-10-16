import cv2, sys, os
base='/home/user/quantiphy-challenge/data/QuantiPhy/captured_0032%s.mp4'
out='/home/user/quantiphy-challenge/research/next/labaudit/0032/frames'
for s in ['', 's', 'x']:
    c = cv2.VideoCapture(base % s)
    i = 0
    while True:
        ok, f = c.read()
        if not ok: break
        cv2.imwrite(os.path.join(out, 'o' if s=='' else s) + '_%02d.png' % i, f)
        i += 1
    print(s, i)
