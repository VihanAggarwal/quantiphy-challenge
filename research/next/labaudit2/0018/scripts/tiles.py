import sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0018/scripts')
from common import *
r, x0, x1, y0, y1, scale, name = sys.argv[1], *map(int, sys.argv[2:6]), float(sys.argv[6]), sys.argv[7]
ks = [int(a) for a in sys.argv[8:]]
fr = frames(r if r != 'o' else '')
tiles = []
for k in ks:
    t = fr[k][y0:y1, x0:x1].copy()
    t = cv2.resize(t, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
    # grid every 10 px
    for x in range(x0 - x0 % 10 + 10, x1, 10):
        X = int((x - x0) * scale); cv2.line(t, (X, 0), (X, 4 if x % 50 else 12), (0, 0, 255), 1)
    for y in range(y0 - y0 % 10 + 10, y1, 10):
        Y = int((y - y0) * scale); cv2.line(t, (0, Y), (4 if y % 50 else 12, Y), (0, 0, 255), 1)
    cv2.putText(t, str(k), (5, 22), 0, 0.7, (0, 0, 255), 2)
    tiles.append(t)
im = np.concatenate(tiles, 1)
cv2.imwrite(OUT + 'img/' + name + '.png', im)
print(im.shape)
