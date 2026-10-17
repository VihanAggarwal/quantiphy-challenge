import cv2, numpy as np
r = np.load('t66.npy')
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0066.mp4')
tiles = []
for fr in (55, 60, 65):
    c.set(cv2.CAP_PROP_POS_FRAMES, fr); ok, im = c.read()
    row = r[r[:, 0] == fr][0]; x, y = int(row[1]), int(row[2])
    cr = im[y - 200:y + 200, x - 220:x + 220].copy()
    for yy in range(0, 400, 20):
        cv2.line(cr, (0, yy), (8 if yy % 100 else 20, yy), (0, 255, 0), 2)
    cv2.putText(cr, '%d y0=%d' % (fr, y - 200), (5, 390), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    tiles.append(cr)
cv2.imwrite('/home/user/quantiphy-challenge/research/next/audit3/internet_03/c66ball.png', np.hstack(tiles))
