import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0121_segmented.mp4')
i = 0
while True:
    ok, im = c.read()
    if not ok: break
    g = im.astype(np.float32)
    d = 255 - g.min(axis=2)
    m = (d > 30).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    out = ['x%d-%d(%d) y%d-%d(%d) a%d c%.1f,%.1f' % (s[0], s[0]+s[2], s[2], s[1], s[1]+s[3], s[3], s[4], ce[0], ce[1]) for s, ce in zip(st[1:], cen[1:]) if s[4] > 300]
    print(i, ' | '.join(out))
    i += 1
