"""Track the white ball in the o and s renders by difference from a background median; circle fit on the blob."""
import cv2, numpy as np, json
B = '/home/user/quantiphy-challenge/research/next/labaudit/0039'
S = '/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
res = {}
for r in ['0039', '0039s', '0039x']:
    fr = np.load(f'{S}/fr_{r}.npy').astype(np.int16)
    bg_late = np.median(fr[0:14], axis=0)   # ball at rest far back; good background for the front part of the table
    bg_early = np.median(fr[44:49], axis=0)  # ball gone
    out = {}
    for i in range(18, 44):
        bg = bg_early
        d = np.abs(fr[i] - bg).sum(-1)
        m = (d > 60).astype(np.uint8)
        m[:400] = 0; m[560:] = 0; m[:, 620:] = 0; m[:, :380] = 0
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(m)
        if n < 2: continue
        k = 1 + np.argmax(st[1:, 4])
        blob = (lab == k).astype(np.uint8)
        cnts, _ = cv2.findContours(blob, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        c = max(cnts, key=cv2.contourArea)
        (ex, ey), (MA, ma), ang = cv2.fitEllipse(c) if len(c) >= 5 else ((0, 0), (0, 0), 0)
        out[i] = dict(c=[float(cen[k][0]), float(cen[k][1])], e=[ex, ey], axes=[min(MA, ma), max(MA, ma)], ang=ang,
                      bbox=[int(v) for v in st[k, :4]], area=int(st[k, 4]))
    res[r] = out
    for i in sorted(out):
        o = out[i]
        print(r, i, 'cen %.1f %.1f' % tuple(o['c']), 'ell %.1f %.1f' % tuple(o['e']), 'axes %.1f %.1f' % tuple(o['axes']), 'bbox', o['bbox'])
json.dump(res, open(f'{B}/track.json', 'w'), indent=1)
