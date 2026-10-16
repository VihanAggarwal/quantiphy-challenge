import cv2, sys, os
out = os.path.dirname(os.path.abspath(__file__))
for v in ['captured_0023','captured_0023s','captured_0023x']:
    c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4' % v)
    i = 0
    while True:
        ok, f = c.read()
        if not ok: break
        cv2.imwrite(os.path.join(out, 'f_%s_%02d.png' % (v.split('_')[1], i)), f)
        i += 1
    print(v, i)
