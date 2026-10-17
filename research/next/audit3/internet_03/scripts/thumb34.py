import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0034.mp4')
c.set(cv2.CAP_PROP_POS_FRAMES, 52); ok, im = c.read()   # full 4K
cr = im[1360:1600, 2000:2320].copy()
cr = cv2.resize(cr, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
for x in range(0, cr.shape[1], 20):
    cv2.line(cr, (x, 0), (x, 8 if x % 100 else 22), (0, 0, 255), 2)
for y in range(0, cr.shape[0], 20):
    cv2.line(cr, (0, y), (8 if y % 100 else 22, y), (0, 0, 255), 2)
cv2.imwrite('/home/user/quantiphy-challenge/research/next/audit3/internet_03/c34thumb.png', cr)
