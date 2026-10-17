import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0059.mp4')
c.set(cv2.CAP_PROP_POS_FRAMES, 78); ok, im = c.read()
cr = im[230:720, 400:1450].copy()
cr = cv2.convertScaleAbs(cr, alpha=1.5, beta=-40)
for x in range(0, cr.shape[1], 50):
    cv2.line(cr, (x, 0), (x, 12 if x % 100 else 25), (0, 0, 255), 2)
    if x % 100 == 0: cv2.putText(cr, str(400 + x), (x + 2, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
for y in range(0, cr.shape[0], 50):
    cv2.line(cr, (0, y), (12 if y % 100 else 25, y), (0, 0, 255), 2)
    if y % 100 == 0: cv2.putText(cr, str(230 + y), (28, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
cv2.imwrite('/home/user/quantiphy-challenge/research/next/audit3/internet_03/c59post.png', cr)
