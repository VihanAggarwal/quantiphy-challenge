"""Apparent sizes (ellipse minor axis = across the blur direction) of the green and white balls in bx and ax."""
import cv2, numpy as np, sys
D = '/home/user/quantiphy-challenge/research/next/labaudit/0054/frames/'
def masks(f, render):
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV).astype(int); b, g, r = [f[..., k].astype(int) for k in range(3)]
    bg = ((g > 200) & (r < 80) & (b < 80)) if render == 'ax' else (hsv[..., 2] < 40)
    yel = (~bg) & (hsv[..., 0] >= 18) & (hsv[..., 0] <= 45) & (hsv[..., 1] > 70) & (hsv[..., 2] > 80)
    wh = (~bg) & (hsv[..., 1] < 80) & (hsv[..., 2] > 110)
    return yel, wh
def ell(m, box):
    x0, y0, x1, y1 = box; mm = np.zeros(m.shape, np.uint8); mm[y0:y1, x0:x1] = m[y0:y1, x0:x1]
    mm = cv2.morphologyEx(mm, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    cs = cv2.findContours(mm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]
    if not cs: return None
    c = max(cs, key=cv2.contourArea)
    if len(c) < 5: return None
    (ex, ey), (a1, a2), ang = cv2.fitEllipse(c)
    return ex, ey, min(a1, a2), max(a1, a2), cv2.contourArea(c)
if __name__ == '__main__':
    render = sys.argv[1]
    boxes = eval(sys.argv[2])  # {frame: {'G':(x0,y0,x1,y1),'W':(...)}}
    for n, bb in sorted(boxes.items()):
        f = cv2.imread(D + '%s_%02d.png' % (render, n)); yel, wh = masks(f, render)
        for k, box in bb.items():
            e = ell(yel if k == 'G' else wh, box)
            print(n, k, None if e is None else 'c=(%.1f,%.1f) minor %.1f major %.1f area %.0f' % e)
