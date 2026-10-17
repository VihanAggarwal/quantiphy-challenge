import cv2, numpy as np, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0039/scripts')
from frames import load
r = sys.argv[1]; fs = [int(x) for x in sys.argv[2].split(',')]
fr = load(r)
tiles = []
for i in fs:
    c = fr[i, 420:560, 440:600].copy()
    c = cv2.resize(c, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
    cv2.putText(c, str(i), (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    tiles.append(c)
rows = [np.hstack(tiles[k:k + 4]) for k in range(0, len(tiles), 4)]
w = max(x.shape[1] for x in rows)
rows = [np.pad(x, ((0, 0), (0, w - x.shape[1]), (0, 0))) for x in rows]
cv2.imwrite(f'/home/user/quantiphy-challenge/research/next/labaudit2/0039/png/crops_{r}_{fs[0]}.png', np.vstack(rows))
