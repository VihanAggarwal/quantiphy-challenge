import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0034.mp4')
F = []
while True:
    ok, im = c.read()
    if not ok: break
    F.append(cv2.resize(im, (1920, 1080), interpolation=cv2.INTER_AREA))
G = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in F]
def skin(f):
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    return (hsv[..., 1] > 45)
def track(start, box, direction, stop):
    x0, y0, x1, y1 = box
    pos = {start: np.array([(x0 + x1) / 2, (y0 + y1) / 2])}
    i = start
    while i != stop:
        j = i + direction
        mask = np.zeros_like(G[i]); mask[int(y0):int(y1), int(x0):int(x1)] = 255
        mask[skin(F[i])] = 0
        pts = cv2.goodFeaturesToTrack(G[i], 300, 0.005, 7, mask=mask)
        if pts is None: break
        p1, st, err = cv2.calcOpticalFlowPyrLK(G[i], G[j], pts, None, winSize=(31, 31), maxLevel=4)
        p0r, st2, _ = cv2.calcOpticalFlowPyrLK(G[j], G[i], p1, None, winSize=(31, 31), maxLevel=4)
        ok = (st.ravel() == 1) & (np.linalg.norm(p0r - pts, axis=2).ravel() < 1.0)
        dvec = (p1 - pts).reshape(-1, 2)[ok]
        md = np.median(dvec, 0)
        x0 += md[0]; x1 += md[0]; y0 += md[1]; y1 += md[1]
        pos[j] = pos[i] + md
        print(i, '->', j, 'n=%d med=(%.2f,%.2f)' % (ok.sum(), md[0], md[1]))
        i = j
    return pos
box30 = (1070, 520, 1330, 840)
pf = track(30, list(box30), 1, 59)
pb = track(30, list(box30), -1, 8)
pos = {**pb, **pf}
np.save('lk34.npy', np.array([[k, *pos[k]] for k in sorted(pos)]))
