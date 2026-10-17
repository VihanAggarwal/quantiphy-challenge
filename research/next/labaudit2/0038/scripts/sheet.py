import cv2, numpy as np, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0038/scripts')
from common import frames, B
for tag in ('o','x'):
    fr = frames(tag)
    cv2.imwrite(f'{B}/f_{tag}_34.png', fr[34])
    idx = list(range(0, 49, 3))
    th = [cv2.resize(fr[i], (320, 180)) for i in idx]
    for t, i in zip(th, idx): cv2.putText(t, str(i), (5, 20), 0, 0.7, (0, 0, 255), 2)
    while len(th) % 4: th.append(np.zeros_like(th[0]))
    rows = [np.hstack(th[j:j+4]) for j in range(0, len(th), 4)]
    cv2.imwrite(f'{B}/sheet_{tag}.png', np.vstack(rows))
