import cv2, numpy as np, sys
v = sys.argv[1]
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
i = 0
rows = []
while True:
    ok, f = c.read()
    if not ok: break
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    m = ((hsv[...,0] > 95) & (hsv[...,0] < 125) & (hsv[...,1] > 120) & (hsv[...,2] > 80)).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n > 1:
        k = 1 + np.argmax(st[1:, 4])
        x, y, w, h, a = st[k]
        cx, cy = cen[k]
        rows.append((i, x, y, w, h, a, cx, cy))
        print(i, x, y, w, h, a, round(cx,1), round(cy,1))
    i += 1
