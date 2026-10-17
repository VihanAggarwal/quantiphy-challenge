import cv2, numpy as np
O = '/home/user/quantiphy-challenge/research/next/labaudit2/0039/png'
for r in ['0039', '0039x']:
    med = cv2.imread(f'{O}/med_{r}.png')
    for name, (y0, y1, x0, x1), s in [('bottle', (320, 490, 630, 700), 4), ('cup', (365, 505, 715, 805), 4), ('card', (525, 560, 510, 630), 6)]:
        c = cv2.resize(med[y0:y1, x0:x1], None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC)
        for y in range(y0, y1, 10): cv2.line(c, (0, (y - y0) * s), (6, (y - y0) * s), (0, 0, 255), 1); cv2.putText(c, str(y), (8, (y - y0) * s + 4), 0, 0.35, (0, 0, 255), 1)
        for x in range(x0, x1, 10): cv2.line(c, ((x - x0) * s, 0), ((x - x0) * s, 6), (0, 255, 0), 1); cv2.putText(c, str(x), ((x - x0) * s, 16), 0, 0.35, (0, 255, 0), 1)
        cv2.imwrite(f'{O}/{name}_{r}.png', c)
