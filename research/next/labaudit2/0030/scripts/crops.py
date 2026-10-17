import cv2, numpy as np, json, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0030/scripts')
from track import frames
r = sys.argv[1]; key = {'': 'o', 's': 's', 'x': 'x'}[r]
ks = [int(k) for k in sys.argv[2].split(',')]
out = sys.argv[3]
tr = json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0030/track.json'))[key]
trs = json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0030/track.json'))['s']
fr = frames(r)
tiles = []
for k in ks:
    t = tr[k] or trs[k]
    cx, cy = int(round(t['cx'])), int(round(t['cy']))
    h = 50
    im = fr[k].copy()
    crop = im[max(cy-h,0):cy+h, max(cx-h,0):cx+h]
    crop = cv2.resize(crop, None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST)
    ox, oy = max(cx-h,0), max(cy-h,0)
    for kk, col in [('cx', (0,255,0))]:
        px, py = (t['cx']-ox)*4, (t['cy']-oy)*4
        cv2.drawMarker(crop, (int(px), int(py)), col, cv2.MARKER_CROSS, 20, 1)
    cv2.putText(crop, f'v{k}', (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)
    tiles.append(crop)
W = max(t.shape[1] for t in tiles); H = max(t.shape[0] for t in tiles)
tiles = [cv2.copyMakeBorder(t, 0, H-t.shape[0], 0, W-t.shape[1], cv2.BORDER_CONSTANT) for t in tiles]
n = 4
rows = [np.hstack(tiles[i:i+n] + [np.zeros_like(tiles[0])]*(n-len(tiles[i:i+n]))) for i in range(0, len(tiles), n)]
cv2.imwrite(out, np.vstack(rows))
