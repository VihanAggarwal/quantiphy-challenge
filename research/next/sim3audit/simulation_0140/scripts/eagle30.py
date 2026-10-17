import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0030_segmented.mp4')
tr = []
i = 0
while True:
    ok, f = c.read()
    if not ok: break
    g = f.astype(int).sum(2)
    m = (g < 300).astype(np.uint8); m[440:] = 0  # sky region only (island top ~380 but island is light)
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n > 1:
        k = 1 + np.argmax(st[1:, 4])
        x, y, w, h, a = st[k]
        if a > 15: tr.append((i, cen[k][0], cen[k][1], w, h, a))
    i += 1
tr = np.array(tr)
for r in tr: print(int(r[0]), round(r[1],1), round(r[2],1), int(r[3]), int(r[4]), int(r[5]))
np.save('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/eagle30.npy', tr)
