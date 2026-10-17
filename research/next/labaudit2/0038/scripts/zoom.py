import cv2, numpy as np, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0038/scripts')
from common import frames, B
tag = sys.argv[1]; ks = [int(a) for a in sys.argv[2].split(',')]; x0, y0, w, h, z = [int(a) for a in sys.argv[3].split(',')]
fr = frames(tag)
tiles = []
for k in ks:
    c = cv2.resize(fr[k][y0:y0+h, x0:x0+w], (w*z, h*z), interpolation=cv2.INTER_NEAREST)
    for gx in range(0, w, 10): c[:, gx*z] = (0, 255, 0) if gx % 50 == 0 else c[:, gx*z]
    for gy in range(0, h, 10): c[gy*z, :] = (0, 255, 0) if gy % 50 == 0 else c[gy*z, :]
    cv2.putText(c, f'{tag}{k}', (3, 15), 0, 0.5, (0, 0, 255), 1)
    tiles.append(c)
cv2.imwrite(f'{B}/{sys.argv[4]}', np.hstack(tiles))
