import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0034.mp4')
tiles = []
for fr, (x0, y0) in [(45, None), (52, (2000, 1360)), (58, None)]:
    c.set(cv2.CAP_PROP_POS_FRAMES, fr); ok, im = c.read()
    if x0 is None:
        # locate thumb via skin mask near expected place: use frame-specific guess from lk centre offset
        pass
    tiles.append((fr, im))
# frame 52 crop with CLAHE
fr, im = tiles[1]
cr = im[1400:1580, 2080:2300].copy()
lab = cv2.cvtColor(cr, cv2.COLOR_BGR2LAB); cl = cv2.createCLAHE(3.0, (4, 4)); lab[..., 0] = cl.apply(lab[..., 0]); cr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
cr = cv2.resize(cr, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
for x in range(0, cr.shape[1], 40):
    cv2.line(cr, (x, 0), (x, 10 if x % 200 else 30), (0, 0, 255), 2)
for y in range(0, cr.shape[0], 40):
    cv2.line(cr, (0, y), (10 if y % 200 else 30, y), (0, 0, 255), 2)
cv2.imwrite('/home/user/quantiphy-challenge/research/next/audit3/internet_03/c34thumb.png', cr)
print(cr.shape)
