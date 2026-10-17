import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0059.mp4')
W=[];H=[]
for fr in range(0, 123, 6):
    c.set(cv2.CAP_PROP_POS_FRAMES, fr); ok, im = c.read()
    b = im[..., 0].astype(float) - 0.5 * im[..., 2].astype(float)  # blue minus red: plate (gray) vs tan
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(float)
    sub = g[940:1080, 820:980]
    # locate plate: bright & bluish; use gray > median+10 and b-channel test
    sb = b[940:1080, 820:980]
    m = ((sub > np.median(sub) + 12) & (sb > np.median(sb) - 3)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n < 2: continue
    k = 1 + np.argmax(st[1:, 4]); x, y, w, h, a = st[k]
    cx, cy = int(cen[k][0]), int(cen[k][1])
    # gradient edges
    rowp = sub[cy - 10:cy + 10, :].mean(0); colp = sub[:, max(0,cx - 8):cx + 8].mean(1)
    dr = np.diff(rowp); dc = np.diff(colp)
    L = np.argmax(dr[:cx]); R = cx + np.argmin(dr[cx:])
    T = np.argmax(dc[:cy]); B = cy + np.argmin(dc[cy:])
    W.append(R - L); H.append(B - T)
    print(fr, 'bbox', w, h, 'grad w=%d h=%d  T=%d B=%d' % (R - L, B - T, T + 940, B + 940), 'edgeB' if B + 940 >= 1078 else '')
print('median w', np.median(W), 'h', np.median(H))
