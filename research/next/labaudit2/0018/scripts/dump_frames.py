import sys, cv2
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0018/scripts')
from common import *
fr = frames('')
for k in [int(a) for a in sys.argv[1:]]:
    im = fr[k].copy()
    for x in range(0, 1280, 100): cv2.line(im, (x, 0), (x, 719), (0, 255, 255), 1)
    for y in range(0, 720, 100): cv2.line(im, (0, y), (1279, y), (0, 255, 255), 1)
    cv2.putText(im, str(k), (10, 40), 0, 1.3, (0, 0, 255), 3)
    cv2.imwrite(OUT + f'img/full_{k:02d}.png', im)
