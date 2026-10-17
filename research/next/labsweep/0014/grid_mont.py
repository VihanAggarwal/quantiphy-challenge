import cv2, sys, numpy as np
# usage: grid_mont.py video x0 y0 x1 y1 scale out frames...
v = sys.argv[1]; x0, y0, x1, y1, s = map(int, sys.argv[2:7]); out = sys.argv[7]
frames = [int(a) for a in sys.argv[8:]]
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4' % v)
fr = []
while True:
    ok, f = c.read()
    if not ok: break
    fr.append(f)
tiles = []
for fi in frames:
    cr = cv2.resize(fr[fi][y0:y1, x0:x1], None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC)
    for x in range((x0 // 5 + 1) * 5, x1, 5):
        X = (x - x0) * s
        L = 12 if x % 10 == 0 else 5
        cv2.line(cr, (X, 0), (X, L), (0, 0, 255), 1); cv2.line(cr, (X, cr.shape[0] - 1), (X, cr.shape[0] - 1 - L), (0, 0, 255), 1)
        if x % 20 == 0: cv2.putText(cr, str(x), (X - 10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    for y in range((y0 // 5 + 1) * 5, y1, 5):
        Y = (y - y0) * s
        L = 12 if y % 10 == 0 else 5
        cv2.line(cr, (0, Y), (L, Y), (0, 0, 255), 1); cv2.line(cr, (cr.shape[1] - 1, Y), (cr.shape[1] - 1 - L, Y), (0, 0, 255), 1)
        if y % 20 == 0: cv2.putText(cr, str(y), (14, Y + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    cv2.putText(cr, 'f%d' % fi, (cr.shape[1] - 40, cr.shape[0] - 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    tiles.append(cr)
n = len(tiles); cols = min(n, int(sys.argv[-1]) if False else 4)
while len(tiles) % cols: tiles.append(np.zeros_like(tiles[0]))
rows = [np.hstack(tiles[k:k + cols]) for k in range(0, len(tiles), cols)]
cv2.imwrite(out, np.vstack(rows))
