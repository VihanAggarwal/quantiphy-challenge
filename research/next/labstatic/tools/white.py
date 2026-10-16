import sys, cv2, numpy as np
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[1]))
from frames import read_all
vid = sys.argv[1]; n0, n1 = int(sys.argv[2]), int(sys.argv[3])
roi = tuple(int(x) for x in sys.argv[4].split(','))
vmin = int(sys.argv[5]) if len(sys.argv) > 5 else 200
fr = read_all(vid)
bg = np.median(np.stack(fr[::4]), axis=0).astype(np.int16)
for n in range(n0, n1 + 1):
    f = fr[n].astype(np.int16)
    diff = np.abs(f - bg).max(axis=2)
    hsv = cv2.cvtColor(fr[n], cv2.COLOR_BGR2HSV)
    m = ((hsv[..., 2] > vmin) & (hsv[..., 1] < 70) & (diff > 40)).astype(np.uint8)
    x0, y0, x1, y1 = roi; mm = np.zeros_like(m); mm[y0:y1, x0:x1] = m[y0:y1, x0:x1]; m = mm
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    k, lab, st, cen = cv2.connectedComponentsWithStats(m)
    cs = [(st[i, 4], cen[i], st[i]) for i in range(1, k) if 15 < st[i, 4] < 3000]
    if cs:
        a, c, s = max(cs, key=lambda z: z[0])
        print(n, round(c[0], 1), round(c[1], 1), 'wh', s[2], s[3], 'area', a)
    else:
        print(n, '-')
