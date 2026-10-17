"""Crop montage around the ball for given frames, with round-1 centroid marked."""
import cv2, json, numpy as np, sys
R = sys.argv[1]; frames = [int(x) for x in sys.argv[2].split(',')]; out = sys.argv[3]
half = int(sys.argv[4]) if len(sys.argv) > 4 else 80; scale = float(sys.argv[5]) if len(sys.argv) > 5 else 2.0
base = '/home/user/quantiphy-challenge/research/next/labaudit/0040'
tr = json.load(open(f'{base}/track_{"x" if R=="o" else R}.json'))
tiles = []
for i in frames:
    im = cv2.imread(f'{base}/frames/v{R}_{i:02d}.png')
    u, v = tr[str(i)]['u'], tr[str(i)]['v']
    x0, y0 = int(round(u)) - half, int(round(v)) - half
    pad = cv2.copyMakeBorder(im, half, half, half, half, cv2.BORDER_CONSTANT)
    c = pad[y0 + half:y0 + 3 * half, x0 + half:x0 + 3 * half].copy()
    c = cv2.resize(c, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
    cc = (int((u - x0) * scale), int((v - y0) * scale))
    cv2.drawMarker(c, cc, (0, 0, 255), cv2.MARKER_CROSS, 10, 1)
    cv2.putText(c, f'{i} ({u:.0f},{v:.0f})', (4, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1)
    tiles.append(c)
ncol = int(sys.argv[6]) if len(sys.argv) > 6 else 4
while len(tiles) % ncol: tiles.append(np.zeros_like(tiles[0]))
rows = [np.hstack(tiles[k:k + ncol]) for k in range(0, len(tiles), ncol)]
cv2.imwrite(out, np.vstack(rows))
