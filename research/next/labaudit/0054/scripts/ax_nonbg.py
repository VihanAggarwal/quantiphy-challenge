"""ax (chroma-key green bg): every non-background blob in a box -> ellipse fit; prints crops for visual check."""
import cv2, numpy as np, sys
D = '/home/user/quantiphy-challenge/research/next/labaudit/0054/frames/'
OUT = '/home/user/quantiphy-challenge/research/next/labaudit/0054/'
frames = range(int(sys.argv[1]), int(sys.argv[2])); x0, y0, x1, y1 = [int(a) for a in sys.argv[3:7]]
tiles = []
for n in frames:
    f = cv2.imread(D + 'ax_%02d.png' % n); b, g, r = [f[..., k].astype(int) for k in range(3)]
    fg = ~((g > 150) & (g - r > 80) & (g - b > 80))
    m = np.zeros(fg.shape, np.uint8); m[y0:y1, x0:x1] = fg[y0:y1, x0:x1]
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    cs = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]
    desc = []
    for c in sorted(cs, key=cv2.contourArea, reverse=True)[:4]:
        if len(c) < 5 or cv2.contourArea(c) < 30: continue
        (ex, ey), (a1, a2), ang = cv2.fitEllipse(c)
        mm = np.zeros_like(m); cv2.drawContours(mm, [c], -1, 1, -1)
        col = f[mm.astype(bool)].mean(0)
        desc.append('(%.1f,%.1f) minor %.1f major %.1f area %.0f BGR %s' % (ex, ey, min(a1, a2), max(a1, a2), cv2.contourArea(c), np.round(col).astype(int)))
    print(n, ' | '.join(desc))
    t = cv2.resize(f[y0:y1, x0:x1], None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST); cv2.putText(t, str(n), (3, 15), 0, 0.5, (0, 0, 255), 1)
    tiles.append(t)
while len(tiles) % 4: tiles.append(np.zeros_like(tiles[0]))
cv2.imwrite(OUT + 'ax_nonbg_%s_%s.png' % (sys.argv[1], sys.argv[2]), np.vstack([np.hstack(tiles[k:k + 4]) for k in range(0, len(tiles), 4)]))
