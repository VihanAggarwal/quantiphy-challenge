# Zoomed crops of jar and toy at video frames 11-21 with round-1 track centroid marked (visual check)
import sys; sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0020/scripts')
from common import *
T = json.load(open(ROOT + '/research/next/labaudit/0020/tracks.json'))
r = sys.argv[1] if len(sys.argv) > 1 else 'o'
obj = sys.argv[2] if len(sys.argv) > 2 else 'jar'
ks = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else list(range(11, 21))
fr = frames(r)
tiles = []
half = 40; z = 4
for k in ks:
    tr = T[r][obj].get(str(k))
    if tr is None: continue
    u, v = tr[0], tr[1]
    x0 = int(round(u)) - half; y0 = int(round(v)) - half
    im = fr[k]
    pad = cv2.copyMakeBorder(im, 100, 100, 100, 100, cv2.BORDER_CONSTANT)
    c = pad[y0 + 100:y0 + 100 + 2 * half, x0 + 100:x0 + 100 + 2 * half].copy()
    c = cv2.resize(c, None, fx=z, fy=z, interpolation=cv2.INTER_NEAREST)
    cu = (u - x0) * z; cv_ = (v - y0) * z
    cv2.drawMarker(c, (int(cu), int(cv_)), (0, 0, 255), cv2.MARKER_CROSS, 20, 2)
    cv2.putText(c, f'{r}{k} ({u:.0f},{v:.0f})', (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    tiles.append(c)
rows = [np.hstack(tiles[i:i + 5] + [np.zeros_like(tiles[0])] * (5 - len(tiles[i:i + 5]))) for i in range(0, len(tiles), 5)]
out = np.vstack(rows)
cv2.imwrite(D + f'img/crops_{r}_{obj}.png', out)
print(out.shape)
