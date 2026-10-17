import cv2, numpy as np, sys
B = '/home/user/quantiphy-challenge/research/next/labaudit2/0038'
img = cv2.imread(f'{B}/median_{sys.argv[1]}.png')
x0, y0, w, h, z = [int(a) for a in sys.argv[2].split(',')]
c = cv2.resize(img[y0:y0+h, x0:x0+w], (w*z, h*z), interpolation=cv2.INTER_NEAREST)
for gx in range(0, w, 10): c[:, gx*z] = (0, 255, 0) if (x0+gx) % 50 == 0 else (0, 120, 0)
for gy in range(0, h, 10): c[gy*z, :] = (0, 255, 0) if (y0+gy) % 50 == 0 else (0, 120, 0)
cv2.putText(c, f'x0={x0} y0={y0} grid10', (3, 15), 0, 0.5, (0, 0, 255), 1)
cv2.imwrite(f'{B}/{sys.argv[3]}', c)
