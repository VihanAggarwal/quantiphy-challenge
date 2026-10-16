"""Soccer ball track: bx (black bg; the ball turns into a dark grey disc after n~31) and ax (green bg)."""
import cv2, numpy as np, sys
D = '/home/user/quantiphy-challenge/research/next/labaudit/0054/frames/'
def soccer_bx(i):
    f = cv2.imread(D + 'bx_%02d.png' % i)
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV).astype(int)
    m = ((hsv[..., 2] > 6) & (hsv[..., 1] < 60)).astype(np.uint8); m[688:] = 0
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
    k = 1 + np.argmax(st[1:, 4])
    c = max(cv2.findContours((lab == k).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0], key=cv2.contourArea)
    (ex, ey), (MA, ma), ang = cv2.fitEllipse(c) if len(c) >= 5 else ((0, 0), (0, 0), 0)
    return cen[k], st[k, 4], st[k, 2], st[k, 3], (ex, ey, min(MA, ma), max(MA, ma))
def soccer_ax(i):
    f = cv2.imread(D + 'ax_%02d.png' % i)
    b, g, r = [f[..., k].astype(int) for k in range(3)]
    bg = (g > 200) & (r < 80) & (b < 80)
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV).astype(int)
    m = (~bg) & (hsv[..., 1] < 50) & (hsv[..., 2] > 150)
    sub = np.zeros_like(m); sub[480:720, 0:330] = True
    m = (m & sub).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
    if n < 2: return None
    k = 1 + np.argmax(st[1:, 4])
    return cen[k], st[k, 4], st[k, 2], st[k, 3], (st[k, 0], st[k, 1])
if __name__ == '__main__':
    for i in range(0, 49):
        c, a, w, h, e = soccer_bx(i)
        r = soccer_ax(i)
        sa = '' if r is None else 'ax c=(%.1f,%.1f) a%d %dx%d x0y0=%s' % (r[0][0], r[0][1], r[1], r[2], r[3], r[4])
        print('%2d bx c=(%.1f,%.1f) a%d %dx%d ell minor %.1f major %.1f | %s' % (i, c[0], c[1], a, w, h, e[2], e[3], sa))
