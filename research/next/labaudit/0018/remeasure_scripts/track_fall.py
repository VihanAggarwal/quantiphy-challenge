import numpy as np, cv2, sys
fr = np.load('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/fr0018.npy').astype(np.float32)
# background: frame 0..? box/ball present early; use frames 44-48 (objects on floor/rolled) for upper region
bg = np.median(fr[44:49], axis=0)
out = []
for i in range(26, 44):
    d = np.abs(fr[i] - bg).sum(2)
    g = fr[i].mean(2)
    hsv = cv2.cvtColor(fr[i].astype(np.uint8), cv2.COLOR_BGR2HSV)
    mask = ((d > 60) & (hsv[..., 1] < 60)).astype(np.uint8)
    # restrict to region x 440..640, y 220..640
    m = np.zeros_like(mask); m[220:640, 440:660] = mask[220:640, 440:660]
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    comps = [(st[k, 4], st[k, 0], st[k, 1], st[k, 2], st[k, 3], cen[k][0], cen[k][1]) for k in range(1, n) if st[k, 4] > 80]
    comps.sort(key=lambda c: -c[0])
    print(i, [(a, x, y, w, h, round(cx, 1), round(cy, 1)) for a, x, y, w, h, cx, cy in comps[:4]])
    vis = fr[i].astype(np.uint8).copy(); vis[m > 0] = (0, 0, 255)
    cv2.imwrite('/home/user/quantiphy-challenge/research/next/labaudit/0018/remeasure_frames/seg_%02d.png' % i, vis[200:660, 420:680])
