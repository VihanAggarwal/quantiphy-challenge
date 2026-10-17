import cv2, numpy as np, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0038/scripts')
from common import frames, B
for tag in ('o', 's', 'x'):
    fr = frames(tag)
    cv2.imwrite(f'{B}/median_{tag}.png', np.median(fr, axis=0).astype(np.uint8))
