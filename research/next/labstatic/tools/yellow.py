import sys, cv2, numpy as np
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[1]))
from frames import read_all
vid = sys.argv[1]; n0, n1 = int(sys.argv[2]), int(sys.argv[3])
hlo, hhi, smin = (int(x) for x in (sys.argv[4] if len(sys.argv) > 4 else '20,35,120').split(','))
roi = tuple(int(x) for x in sys.argv[5].split(',')) if len(sys.argv) > 5 else None
fr = read_all(vid)
for n in range(n0, n1 + 1):
    hsv = cv2.cvtColor(fr[n], cv2.COLOR_BGR2HSV)
    m = ((hsv[..., 0] >= hlo) & (hsv[..., 0] <= hhi) & (hsv[..., 1] > smin) & (hsv[..., 2] > 90)).astype(np.uint8)
    if roi:
        x0, y0, x1, y1 = roi; mm = np.zeros_like(m); mm[y0:y1, x0:x1] = m[y0:y1, x0:x1]; m = mm
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    k, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if k > 1:
        i = 1 + np.argmax(st[1:, 4])
        x, y, w, h, a = st[i]
        print(n, round(cen[i][0], 1), round(cen[i][1], 1), 'bbox', x, y, x + w, y + h, 'wh', w, h, 'area', a)
