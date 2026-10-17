import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0133.mp4')
i = 0
rows = []
while True:
    ok, im = c.read()
    if not ok: break
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    m = ((hsv[..., 1] > 90) & (hsv[..., 2] > 40)).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n > 1:
        k = 1 + np.argmax(st[1:, 4])
        s = st[k]; ce = cen[k]
        rows.append((i, ce[0], ce[1], s[0], s[0]+s[2], s[1], s[1]+s[3], s[4]))
        print('%d c%.1f,%.1f x%d-%d(%d) y%d-%d(%d) a%d' % (i, ce[0], ce[1], s[0], s[0]+s[2], s[2], s[1], s[1]+s[3], s[3], s[4]))
    i += 1
np.save('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/apple.npy', np.array(rows))
