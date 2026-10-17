"""Zoomed crops (x6) of the ball with the tracked centre marked, for visual verification."""
import sys, json, cv2, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0022/scripts')
from common import *
T = json.load(open(f'{B}/track.json'))
tag = sys.argv[1]; ks = [int(a) for a in sys.argv[2].split(',')]; S = 6; hw = 16
fr = frames(tag); tiles = []
for k in ks:
    u, v = T[tag][k][:2]; u0, v0 = int(round(u)), int(round(v))
    c = cv2.resize(fr[k][v0 - hw:v0 + hw, u0 - hw:u0 + hw], None, fx=S, fy=S, interpolation=cv2.INTER_CUBIC)
    px = ((u - (u0 - hw) + 0.5) * S, (v - (v0 - hw) + 0.5) * S)
    cv2.drawMarker(c, (int(px[0]), int(px[1])), (0, 0, 255), cv2.MARKER_CROSS, 14, 1)
    cv2.putText(c, str(k), (3, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    tiles.append(c)
cv2.imwrite(f'{B}/img/zoom_{tag}_{sys.argv[3]}.png', np.hstack(tiles))
