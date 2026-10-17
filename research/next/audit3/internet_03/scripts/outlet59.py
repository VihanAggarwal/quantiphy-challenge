import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0059.mp4')
tiles=[]
for fr in (0, 40, 78, 100):
    c.set(cv2.CAP_PROP_POS_FRAMES, fr); ok, im = c.read()
    cr = im[960:1080, 820:980].copy()
    cr = cv2.resize(cr, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    cr = cv2.convertScaleAbs(cr, alpha=1.6, beta=-50)
    for x in range(0, cr.shape[1], 40):
        cv2.line(cr, (x, 0), (x, 10 if x % 200 else 25), (0, 0, 255), 2)
    for y in range(0, cr.shape[0], 40):
        cv2.line(cr, (0, y), (10 if y % 200 else 25, y), (0, 0, 255), 2)
    cv2.putText(cr, str(fr), (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    tiles.append(cr)
cv2.imwrite('/home/user/quantiphy-challenge/research/next/audit3/internet_03/c59outlet.png', np.hstack(tiles))
