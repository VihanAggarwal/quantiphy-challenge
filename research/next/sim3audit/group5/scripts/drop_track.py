import cv2, numpy as np, json
cap = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0201.mp4')
fr = []
while True:
    ok, f = cap.read()
    if not ok: break
    fr.append(f)
bg = np.median(np.stack(fr[11:14]).astype(np.float32), 0)
out = []
for i in range(12):
    d = np.abs(fr[i].astype(np.float32) - bg).sum(2)
    d = cv2.GaussianBlur(d, (5, 5), 0)
    m = (d > 30).astype(np.uint8)
    # restrict to region right of the dropper tip / below
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    best = None
    for k in range(1, n):
        x, y, w, h, a = st[k]
        if a < 200: continue
        if best is None or a > st[best][4]: best = k
    if best is None:
        print(i, 'none'); continue
    x, y, w, h, a = st[best]
    ys, xs = np.where(lab == best)
    out.append(dict(i=i, cx=float(xs.mean()), cy=float(ys.mean()), x0=int(x), x1=int(x + w), y0=int(y), y1=int(y + h), w=int(w), h=int(h), area=int(a)))
    print(i, round(xs.mean(), 1), round(ys.mean(), 1), x, y, w, h, a)
json.dump(out, open('/home/user/quantiphy-challenge/research/next/sim3audit/group5/drop_track.json', 'w'), indent=1)
