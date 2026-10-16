import cv2, numpy as np, sys
B = '/home/user/quantiphy-challenge/research/next/labaudit/0038'
src, x0, y0, x1, y1, s, out = sys.argv[1], *map(int, sys.argv[2:7]), sys.argv[7]
m = cv2.imread(f'{B}/{src}')
c = m[y0:y1, x0:x1]
c = cv2.resize(c, None, fx=s, fy=s, interpolation=cv2.INTER_NEAREST)
step = int(sys.argv[8]) if len(sys.argv) > 8 else 10
for x in range((x0 // step + 1) * step, x1, step):
    cv2.line(c, ((x - x0) * s, 0), ((x - x0) * s, 6), (0, 0, 255), 1)
    if x % (step*5) == 0: cv2.putText(c, str(x), ((x - x0) * s + 2, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
for y in range((y0 // step + 1) * step, y1, step):
    cv2.line(c, (0, (y - y0) * s), (6, (y - y0) * s), (0, 0, 255), 1)
    if y % (step*5) == 0: cv2.putText(c, str(y), (8, (y - y0) * s + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
cv2.imwrite(f'{B}/{out}', c)
