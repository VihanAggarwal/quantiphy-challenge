# Zoomed crops (x and o renders) of jar or toy for chosen video frames, from my own track (track2.json), 6x zoom
import sys; sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0020/scripts')
from common import *
T2 = json.load(open(D + 'track2.json'))
r = sys.argv[1]; obj = sys.argv[2]; ks = [int(x) for x in sys.argv[3].split(',')]; half = int(sys.argv[4]) if len(sys.argv) > 4 else 30
z = 6; fr = frames(r); tiles = []
for k in ks:
    u, v = T2[r][obj][str(k)]['c']
    x0 = int(round(u)) - half; y0 = int(round(v)) - half
    pad = cv2.copyMakeBorder(fr[k], 100, 100, 100, 100, cv2.BORDER_CONSTANT)
    c = pad[y0 + 100:y0 + 100 + 2 * half, x0 + 100:x0 + 100 + 2 * half].copy()
    c = cv2.resize(c, None, fx=z, fy=z, interpolation=cv2.INTER_CUBIC)
    for g in range(0, 2 * half * z, 10 * z): cv2.line(c, (g, 0), (g, 8), (0, 0, 255), 1); cv2.line(c, (0, g), (8, g), (0, 0, 255), 1)
    cv2.drawMarker(c, (int((u - x0) * z), int((v - y0) * z)), (0, 0, 255), cv2.MARKER_CROSS, 16, 1)
    cv2.putText(c, f'{r}{k}', (12, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    tiles.append(c)
n = 4
rows = [np.hstack(tiles[i:i + n] + [np.zeros_like(tiles[0])] * (n - len(tiles[i:i + n]))) for i in range(0, len(tiles), n)]
cv2.imwrite(D + f'img/z_{r}_{obj}_{ks[0]}.png', np.vstack(rows))
