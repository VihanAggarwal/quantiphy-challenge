import cv2, numpy as np, json
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0140.mp4')
frames = []
while True:
    ok, f = c.read()
    if not ok: break
    frames.append(cv2.resize(f, (960, 540), interpolation=cv2.INTER_AREA))  # half-res for bg
full = []
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0140.mp4')
# median background at full res, computed on grayscale stack in strips to save memory
grays = []
while True:
    ok, f = c.read()
    if not ok: break
    grays.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY))
G = np.stack(grays)  # 100x1080x1920 uint8 ~ 207MB in RAM only
bg = np.median(G, axis=0).astype(np.int16)
cv2.imwrite('frames/bg140.png', bg.astype(np.uint8))
res = []
for i in range(len(G)):
    d = np.abs(G[i].astype(np.int16) - bg)
    m = (d > 18).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n <= 1:
        res.append(None); continue
    k = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    x,y,w,h,a = st[k]
    ys, xs = np.nonzero(lab == k)
    wts = d[ys, xs].astype(float)
    res.append(dict(i=i, cx=float(cen[k][0]), cy=float(cen[k][1]), wx=float((xs*wts).sum()/wts.sum()), wy=float((ys*wts).sum()/wts.sum()), x=int(x), y=int(y), w=int(w), h=int(h), area=int(a)))
json.dump(res, open('track140.json','w'), indent=0)
for r in res:
    if r: print(r['i'], round(r['cx'],1), round(r['cy'],1), r['x'], r['y'], r['w'], r['h'], r['area'])
    else: print('none')
