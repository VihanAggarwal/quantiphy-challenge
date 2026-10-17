"""Bird blob track (median background subtraction, full res). usage: birdtrack.py video_id x0 y0 x1 y1 [thresh]
Prints per frame: centroid, bbox, area, and dark-core centroid (body) inside a search ROI."""
import sys, cv2, numpy as np, json
vid = sys.argv[1]; x0, y0, x1, y1 = map(int, sys.argv[2:6]); th = float(sys.argv[6]) if len(sys.argv) > 6 else 30
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
fr = []
while True:
    ok, f = c.read()
    if not ok: break
    fr.append(f[y0:y1, x0:x1].astype(np.int16))
fr = np.array(fr)
bg = np.median(fr, axis=0)
out = []
prev = None
for i, f in enumerate(fr):
    d = np.abs(f - bg).max(axis=2)
    m = (d > th).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n < 2:
        out.append(None); continue
    ks = list(range(1, n))
    if prev is not None:
        ks.sort(key=lambda k: -st[k, 4] / (1 + 0.02 * np.hypot(*(cen[k] - prev))))
    else:
        ks.sort(key=lambda k: -st[k, 4])
    k = ks[0]
    prev = cen[k]
    ys, xs = np.nonzero(lab == k)
    out.append(dict(i=i, cx=float(xs.mean() + x0), cy=float(ys.mean() + y0), bx=int(st[k, 0] + x0), by=int(st[k, 1] + y0),
                    bw=int(st[k, 2]), bh=int(st[k, 3]), area=int(st[k, 4])))
json.dump(out, open(f'/home/user/quantiphy-challenge/research/next/sim3audit/group2/{vid}_birdtrack.json', 'w'))
for o in out:
    if o: print(o['i'], round(o['cx'], 1), round(o['cy'], 1), o['bx'], o['by'], o['bw'], o['bh'], o['area'])
