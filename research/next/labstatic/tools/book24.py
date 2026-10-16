import sys, cv2, numpy as np
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[1]))
from frames import read_all
vid = sys.argv[1]
fr = read_all(vid)
f0 = fr[0]
hsv0 = cv2.cvtColor(f0, cv2.COLOR_BGR2HSV)
for n in range(0, len(fr), 1):
    hsv = cv2.cvtColor(fr[n], cv2.COLOR_BGR2HSV)
    m = ((hsv[..., 0] > 70) & (hsv[..., 0] < 100) & (hsv[..., 1] > 35) & (hsv[..., 2] > 100)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    k, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if k > 1:
        i = 1 + np.argmax(st[1:, 4])
        x, y, w, h, a = st[i]
        print(n, round(cen[i][0], 1), round(cen[i][1], 1), 'bbox', x, y, x + w, y + h, 'area', a)
