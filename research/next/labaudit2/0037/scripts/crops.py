"""Zoom crops of the ball around given video frames, with the tracked centroid marked. usage: crops.py render f0 f1 out.png"""
import sys, json, cv2, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0037/scripts')
from common import frames, OUT
r, f0, f1, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
tr = json.load(open(OUT + '/track.json'))[r or 'o']
fr = frames('' if r == 'o' else r)
tiles = []
for i in range(f0, f1 + 1):
    e = tr.get(str(i))
    if e is None:
        cu, cv_ = 640, 360
    else:
        cu, cv_ = e['u'], e['v']
    x0, y0 = int(cu) - 40, int(cv_) - 40
    c = fr[i][max(0, y0):y0 + 80, max(0, x0):x0 + 80].copy()
    c = cv2.resize(c, (320, 320), interpolation=cv2.INTER_NEAREST)
    if e is not None:
        px, py = (e['u'] - x0) * 4, (e['v'] - y0) * 4
        cv2.drawMarker(c, (int(px), int(py)), (0, 0, 255), cv2.MARKER_CROSS, 12, 1)
    cv2.putText(c, 'v%d' % i, (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
    tiles.append(c)
while len(tiles) % 4:
    tiles.append(np.zeros_like(tiles[0]))
rows = [np.hstack(tiles[k:k + 4]) for k in range(0, len(tiles), 4)]
cv2.imwrite(out, np.vstack(rows))
