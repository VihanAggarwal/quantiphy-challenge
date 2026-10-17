"""Zoomed crops with a 10 px grid (labels every 50 px) for chosen frames. usage: crops.py tag x0 y0 w h scale out frames..."""
import cv2, numpy as np, sys
from common import *
tag, x0, y0, w, h, sc, outn = sys.argv[1], *map(int, sys.argv[2:7]), sys.argv[7]
frames = [int(a) for a in sys.argv[8:]]
fr = load(tag); tiles = []
for i in frames:
    c = fr[i][y0:y0 + h, x0:x0 + w]
    c = cv2.resize(c, (w * sc, h * sc), interpolation=cv2.INTER_NEAREST)
    for gx in range((x0 // 10 + 1) * 10, x0 + w, 10):
        col = (0, 0, 255) if gx % 50 == 0 else (90, 90, 90)
        cv2.line(c, ((gx - x0) * sc, 0), ((gx - x0) * sc, h * sc), col, 1)
        if gx % 50 == 0: cv2.putText(c, str(gx), ((gx - x0) * sc + 2, 12), 0, 0.4, (0, 0, 255), 1)
    for gy in range((y0 // 10 + 1) * 10, y0 + h, 10):
        col = (0, 0, 255) if gy % 50 == 0 else (90, 90, 90)
        cv2.line(c, (0, (gy - y0) * sc), (w * sc, (gy - y0) * sc), col, 1)
        if gy % 50 == 0: cv2.putText(c, str(gy), (2, (gy - y0) * sc - 2), 0, 0.4, (0, 0, 255), 1)
    cv2.putText(c, '%s v%d' % (tag, i), (5, h * sc - 8), 0, 0.7, (0, 255, 255), 2)
    tiles.append(c)
cols = 4 if len(tiles) > 4 else len(tiles)
while len(tiles) % cols: tiles.append(np.zeros_like(tiles[0]))
rows = [np.hstack(tiles[r * cols:(r + 1) * cols]) for r in range(len(tiles) // cols)]
cv2.imwrite(D + 'img/' + outn, np.vstack(rows))
