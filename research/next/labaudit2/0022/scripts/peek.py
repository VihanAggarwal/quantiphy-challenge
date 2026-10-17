import sys, cv2; sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0022/scripts')
from common import *
for tag in ['x', 'o']:
    fr = frames(tag)
    for k in [0, 14, 19, 29, 38]:
        cv2.imwrite(f'{B}/img/{tag}_{k:02d}.jpg', fr[k], [cv2.IMWRITE_JPEG_QUALITY, 85])
