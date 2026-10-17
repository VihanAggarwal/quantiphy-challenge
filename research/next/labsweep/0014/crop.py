import cv2, sys, numpy as np
# usage: crop.py video frame x0 y0 x1 y1 scale out [grid]
v, fi, x0, y0, x1, y1, s, out = sys.argv[1:9]
grid = int(sys.argv[9]) if len(sys.argv) > 9 else 10
fi, x0, y0, x1, y1, s = int(fi), int(x0), int(y0), int(x1), int(y1), int(s)
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4' % v)
c.set(cv2.CAP_PROP_POS_FRAMES, fi)
ok, f = c.read()
cr = f[y0:y1, x0:x1]
cr = cv2.resize(cr, None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC)
for x in range((x0 // grid + 1) * grid, x1, grid):
    X = (x - x0) * s
    col = (0, 0, 255) if x % (grid * 5) == 0 else (0, 200, 255)
    cv2.line(cr, (X, 0), (X, 6 if x % (grid*5) else 14), col, 1)
    cv2.line(cr, (X, cr.shape[0]-1), (X, cr.shape[0]-(6 if x % (grid*5) else 14)), col, 1)
    if x % (grid * 5) == 0:
        cv2.putText(cr, str(x), (X + 2, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
for y in range((y0 // grid + 1) * grid, y1, grid):
    Y = (y - y0) * s
    col = (0, 0, 255) if y % (grid * 5) == 0 else (0, 200, 255)
    cv2.line(cr, (0, Y), (6 if y % (grid*5) else 14, Y), col, 1)
    cv2.line(cr, (cr.shape[1]-1, Y), (cr.shape[1]-(6 if y % (grid*5) else 14), Y), col, 1)
    if y % (grid * 5) == 0:
        cv2.putText(cr, str(y), (16, Y + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
cv2.imwrite(out, cr)
