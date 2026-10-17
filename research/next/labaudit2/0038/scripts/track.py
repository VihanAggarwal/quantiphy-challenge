"""Ball track per render: difference from the per-pixel median, white-ish, largest blob in the table band.
Per frame: top edge, bottom (of the bright part), horizontal extent in the band top+0.3R..top+0.9R, centroid.
Writes track.json (small)."""
import cv2, numpy as np, json, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0038/scripts')
from common import frames, B
out = {}
for tag in ('o', 's', 'x'):
    fr = frames(tag).astype(np.int16)
    med = np.median(fr, axis=0)
    rows = []
    for i in range(len(fr)):
        f = fr[i]
        d = np.abs(f - med).sum(-1)
        bright = f.min(-1) > 140
        m = ((d > 50) & bright).astype(np.uint8)
        m[:380] = 0; m[600:] = 0; m[:, :240] = 0
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(m)
        if n < 2: rows.append(None); continue
        k = 1 + np.argmax(st[1:, 4])
        if st[k, 4] < 150: rows.append(None); continue
        ys, xs = np.nonzero(lab == k)
        top, bot = int(ys.min()), int(ys.max())
        H = bot - top + 1
        band = (ys >= top + 0.3 * H) & (ys <= top + 0.6 * H)
        xl, xr = np.percentile(xs[band], 2), np.percentile(xs[band], 98)
        rows.append(dict(f=i, cx=float(cen[k][0]), cy=float(cen[k][1]), top=top, bot=bot, xl=float(xl), xr=float(xr),
                         a=int(st[k, 4]), w=int(st[k, 2]), h=int(st[k, 3])))
    out[tag] = rows
json.dump(out, open(f'{B}/track.json', 'w'))
print(' f  | ' + ' | '.join(f'{t}: umid   top  bot  wid  cx     cy    area' for t in out))
for i in range(49):
    s = f'{i:2d}  '
    for t in out:
        r = out[t][i]
        s += ' | ' + ('-' * 40 if r is None else f"{(r['xl']+r['xr'])/2:6.1f} {r['top']:4d} {r['bot']:4d} {r['xr']-r['xl']:4.1f} {r['cx']:6.1f} {r['cy']:5.1f} {r['a']:5d}")
    print(s)
