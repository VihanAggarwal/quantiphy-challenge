"""Track the white ball by difference from the per-pixel median; report centroid, bbox, blob widths."""
import cv2, numpy as np, json, sys
B = '/home/user/quantiphy-challenge/research/next/labaudit/0038'
out = {}
for tag in ('x', 's', 'o'):
    fr = np.load(f'{B}/frames/{tag}.npy').astype(np.int16)
    med = np.median(fr, axis=0)
    rows = []
    for i in range(len(fr)):
        d = np.abs(fr[i] - med).sum(-1)
        f = fr[i]
        white = (f.min(-1) > 150) & ((f.max(-1) - f.min(-1)) < 60)
        m = ((d > 60) & white).astype(np.uint8)
        m[:300] = 0; m[650:] = 0
        if tag == 'o': m[:, :250] = 0  # person/arm region
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(m)
        if n < 2: rows.append(None); continue
        k = 1 + np.argmax(st[1:, 4])
        x, y, w, h, a = st[k]
        rows.append(dict(f=i, cx=float(cen[k][0]), cy=float(cen[k][1]), x0=int(x), y0=int(y), w=int(w), h=int(h), a=int(a)))
    out[tag] = rows
json.dump(out, open(f'{B}/track.json', 'w'))
for i in range(49):
    s = f'{i:2d} t={i/24:.3f} '
    for tag in ('x', 's', 'o'):
        r = out[tag][i]
        s += ' | ' + ('-' if r is None else f"{r['cx']:7.1f} {r['cy']:6.1f} w{r['w']:3d} h{r['h']:3d} a{r['a']:4d}")
    print(s)
