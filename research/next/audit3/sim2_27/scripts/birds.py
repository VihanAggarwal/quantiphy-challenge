import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0091.mp4')
fr = []
while True:
    ok, im = c.read()
    if not ok: break
    fr.append(im.astype(np.float32))
# background: per-pixel median over frames (birds move fast)
bg = np.median(np.stack(fr[::2]), axis=0)
for i, im in enumerate(fr):
    d = np.abs(im - bg).max(axis=2)
    m = (d > 40).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    objs = [(st[k], cen[k]) for k in range(1, n) if st[k][4] > 30]
    # merge components by proximity: group by x center left/right of mid of the two birds
    out = []
    for s, ce in objs:
        out.append('x%d-%d y%d-%d a%d' % (s[0], s[0]+s[2], s[1], s[1]+s[3], s[4]))
    print(i, ' | '.join(out))
