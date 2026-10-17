import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0034.mp4')
tiles = []
for fr in (15, 30, 45, 52):
    c.set(cv2.CAP_PROP_POS_FRAMES, fr); ok, im = c.read()
    im = cv2.resize(im, (1920, 1080), interpolation=cv2.INTER_AREA)
    cr = im[400:960, 700:1600].copy()
    for x in range(0, 900, 50):
        cv2.line(cr, (x, 0), (x, 10 if x % 100 else 25), (0, 0, 255), 2)
        if x % 100 == 0: cv2.putText(cr, str(700 + x), (x + 2, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    for y in range(0, 560, 50):
        cv2.line(cr, (0, y), (10 if y % 100 else 25, y), (0, 0, 255), 2)
        if y % 100 == 0: cv2.putText(cr, str(400 + y), (28, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    cv2.putText(cr, 'f%d' % fr, (800, 540), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    tiles.append(cr)
cv2.imwrite('/home/user/quantiphy-challenge/research/next/audit3/internet_03/c34roll.png', np.vstack([np.hstack(tiles[:2]), np.hstack(tiles[2:])]))
