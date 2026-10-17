import cv2, numpy as np, sys, json
# usage: track.py video ref_frame x0 y0 x1 y1 [frames spec a:b] [search margin]
v = sys.argv[1]; rf = int(sys.argv[2]); x0, y0, x1, y1 = map(int, sys.argv[3:7])
a, b = map(int, sys.argv[7].split(':')) if len(sys.argv) > 7 else (0, 10**6)
marg = int(sys.argv[8]) if len(sys.argv) > 8 else 10**6
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4' % v)
fr = []
while True:
    ok, im = c.read()
    if not ok: break
    fr.append(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32))
T = fr[rf][y0:y1, x0:x1]
h, w = T.shape
res = {}
prev = (x0, y0)
for i in range(max(0, a), min(len(fr), b)):
    I = fr[i]
    R = cv2.matchTemplate(I, T, cv2.TM_CCOEFF_NORMED)
    _, mv, _, ml = cv2.minMaxLoc(R)
    px, py = ml
    dx = dy = 0.0
    if 0 < px < R.shape[1]-1:
        l, cc, r = R[py, px-1], R[py, px], R[py, px+1]; den = l - 2*cc + r
        dx = 0.5*(l - r)/den if den != 0 else 0
    if 0 < py < R.shape[0]-1:
        u, cc, d = R[py-1, px], R[py, px], R[py+1, px]; den = u - 2*cc + d
        dy = 0.5*(u - d)/den if den != 0 else 0
    res[i] = (px+dx - x0, py+dy - y0, mv)
    print(i, '%.2f %.2f %.3f' % res[i])
