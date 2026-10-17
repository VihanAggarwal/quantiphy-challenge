import cv2, numpy as np, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0039/scripts')
from frames import load
O = '/home/user/quantiphy-challenge/research/next/labaudit2/0039/png'
for r in ['0039', '0039x']:
    fr = load(r)
    med = np.median(fr[0:10], axis=0).astype(np.uint8)
    cv2.imwrite(f'{O}/med_{r}.png', med)
    c = med[400:520, 630:760]; c = cv2.resize(c, None, fx=5, fy=5, interpolation=cv2.INTER_CUBIC)
    for y in range(0, c.shape[0], 50): cv2.line(c, (0, y), (8, y), (0, 0, 255), 1); cv2.putText(c, str(400 + y // 5), (10, y + 4), 0, 0.4, (0, 0, 255), 1)
    for x in range(0, c.shape[1], 50): cv2.line(c, (x, 0), (x, 8), (0, 0, 255), 1); cv2.putText(c, str(630 + x // 5), (x, 20), 0, 0.4, (0, 0, 255), 1)
    cv2.imwrite(f'{O}/poker_{r}.png', c)
