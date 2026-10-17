import sys, cv2, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0022/scripts')
from common import *
tag = sys.argv[1]; ks = [int(a) for a in sys.argv[2].split(',')]; u0, v0, hw, sc = [int(a) for a in sys.argv[3].split(',')]
fr = frames(tag)
tiles = []
for k in ks:
    c = fr[k][v0 - hw:v0 + hw, u0 - hw:u0 + hw]
    c = cv2.resize(c, None, fx=sc, fy=sc, interpolation=cv2.INTER_NEAREST)
    cv2.putText(c, str(k), (3, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    tiles.append(c)
cv2.imwrite(f'{B}/img/{sys.argv[4]}.png', np.hstack(tiles))
