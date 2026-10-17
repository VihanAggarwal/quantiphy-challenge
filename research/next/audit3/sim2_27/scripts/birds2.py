import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0091.mp4')
fr = []
while True:
    ok, im = c.read()
    if not ok: break
    fr.append(im.astype(np.float32))
bg = np.median(np.stack(fr[12:]), axis=0)  # frames 12+ are empty sky
for th in (20, 40, 80):
    print('th', th)
    for i in range(0, 11):
        d = np.abs(fr[i] - bg).max(axis=2)
        m = (d > th).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((2,2),np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(m)
        # crow: components with x center > 1000 (frames <7) ; take union of comps with area>5 in right half
        res = []
        for side, cond in (('eagle', lambda cx: cx < 1000 if i < 7 else False), ('crow', lambda cx: cx >= 1000)):
            ks = [k for k in range(1, n) if st[k][4] > 5 and cond(cen[k][0])]
            if not ks: continue
            x0 = min(st[k][0] for k in ks); x1 = max(st[k][0]+st[k][2] for k in ks)
            y0 = min(st[k][1] for k in ks); y1 = max(st[k][1]+st[k][3] for k in ks)
            ys, xs = np.nonzero(np.isin(lab, ks))
            res.append('%s x%d-%d (%d) y%d-%d (%d) cx%.1f' % (side, x0, x1, x1-x0, y0, y1, y1-y0, xs.mean()))
        print(i, ' | '.join(res))
