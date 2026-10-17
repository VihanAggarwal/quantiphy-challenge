"""Independent tracker for captured_0018 (remeasure_b).
Background = temporal median of all frames; foreground blobs by |frame-bg| plus colour cues.
Outputs blob list per frame (centroid, bbox, area, mean colour) for manual association.
"""
import cv2, numpy as np, json, sys

vid = sys.argv[1] if len(sys.argv) > 1 else 'captured_0018'
path = f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4'
c = cv2.VideoCapture(path)
fr = []
while True:
    ok, f = c.read()
    if not ok:
        break
    fr.append(f)
fr = np.array(fr)
bg_late = np.median(fr[41:49], axis=0).astype(np.uint8)   # objects dropped -> hands empty
bg_early = np.median(fr[0:20], axis=0).astype(np.uint8)   # objects held -> floor empty
out = {}
for i, f in enumerate(fr):
    d1 = np.abs(f.astype(int) - bg_late.astype(int)).sum(2)
    d2 = np.abs(f.astype(int) - bg_early.astype(int)).sum(2)
    d = np.minimum(d1, d2) if 22 <= i <= 40 else (d1 if i < 22 else d2)
    m = (d > 60).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    blobs = []
    for k in range(1, n):
        x, y, w, h, a = st[k]
        if a < 30 or a > 20000:
            continue
        col = f[lab == k].mean(0)
        blobs.append(dict(c=[float(cen[k][0]), float(cen[k][1])], bb=[int(x), int(y), int(w), int(h)], a=int(a),
                          bgr=[round(float(v)) for v in col]))
    out[i] = blobs
json.dump(out, open(f'/home/user/quantiphy-challenge/research/next/labaudit2/0018/remeasure_b/blobs_{vid}.json', 'w'))
for i in range(22, 49):
    print(i, [(round(b['c'][0]), round(b['c'][1]), b['a'], b['bgr']) for b in out[i] if 250 < b['c'][1] < 720 and 350 < b['c'][0] < 1000])
