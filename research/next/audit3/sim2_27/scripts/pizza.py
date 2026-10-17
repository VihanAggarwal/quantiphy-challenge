import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0003_segmented.mp4')
ok, im = c.read()
hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(np.float32)
# pizza crust: orange/tan with saturation; background white (s low, v high)
nonbg = (255 - im.astype(np.float32).min(axis=2)) > 40
# horizontal rows: find leftmost non-bg pixel in the pizza region x in [380, 900]
for y in range(170, 640, 30):
    row = nonbg[y, 380:900]
    xs = np.nonzero(row)[0]
    print(y, (xs.min()+380, xs.max()+380) if len(xs) else None)
for x in range(400, 900, 40):
    col = nonbg[150:650, x]
    ys = np.nonzero(col)[0]
    print('col', x, (ys.min()+150, ys.max()+150) if len(ys) else None)
