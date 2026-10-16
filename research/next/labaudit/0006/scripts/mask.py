"""Yellow-toy mask per frame for captured_0006 / 0006s; prints bbox, area, centroid."""
import cv2, numpy as np, sys
D = '/home/user/quantiphy-challenge/research/next/labaudit/0006/'
def mask(img, hlo=15, hhi=40, smin=90, vmin=90):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    m = cv2.inRange(hsv, (hlo, smin, vmin), (hhi, 255, 255))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n <= 1: return None
    k = 1 + np.argmax(st[1:, 4])
    return (lab == k), st[k], cen[k]
if __name__ == '__main__':
    tag = sys.argv[1] if len(sys.argv) > 1 else '0006'
    for i in range(0, 49):
        img = cv2.imread(D + 'frames/%s_f%02d.png' % (tag, i))
        r = mask(img)
        if r is None: print(i, None); continue
        m, st, c = r
        print(i, 'x%d y%d w%d h%d area%d  c=(%.1f,%.1f)' % (st[0], st[1], st[2], st[3], st[4], c[0], c[1]))
