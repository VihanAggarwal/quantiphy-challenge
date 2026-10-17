import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0034.mp4')
F = []
while True:
    ok, im = c.read()
    if not ok: break
    F.append(cv2.resize(im, (1920, 1080), interpolation=cv2.INTER_AREA))
G = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in F]
skin = lambda f: cv2.cvtColor(f, cv2.COLOR_BGR2HSV)[..., 1] > 45
# roll corners at frame 30 (visual): x 1050-1350, y 505-860 ; use inner box for features, track centre point
def run(start, ctr, box, direction, stop):
    x0, y0, x1, y1 = box
    out = {start: (ctr.copy(), 0.0)}
    ang = 0.0
    i = start
    while i != stop:
        j = i + direction
        mask = np.zeros_like(G[i]); mask[int(y0):int(y1), int(x0):int(x1)] = 255
        mask[skin(F[i])] = 0
        pts = cv2.goodFeaturesToTrack(G[i], 400, 0.005, 6, mask=mask)
        p1, st, _ = cv2.calcOpticalFlowPyrLK(G[i], G[j], pts, None, winSize=(31, 31), maxLevel=4)
        p0r, _, _ = cv2.calcOpticalFlowPyrLK(G[j], G[i], p1, None, winSize=(31, 31), maxLevel=4)
        ok = (st.ravel() == 1) & (np.linalg.norm(p0r - pts, axis=2).ravel() < 1.0)
        M, inl = cv2.estimateAffinePartial2D(pts[ok], p1[ok], method=cv2.RANSAC, ransacReprojThreshold=1.5)
        newc = M[:, :2] @ ctr + M[:, 2]
        d = newc - ctr
        ang += np.degrees(np.arctan2(M[1, 0], M[0, 0]))
        ctr = newc
        x0 += d[0]; x1 += d[0]; y0 += d[1]; y1 += d[1]
        out[j] = (ctr.copy(), ang)
        i = j
    return out
ctr30 = np.array([1200.0, 682.0])
box = [1075, 525, 1330, 845]
o = {**run(30, ctr30, list(box), -1, 8), **run(30, ctr30, list(box), 1, 59)}
for k in sorted(o):
    print(k, 'c=(%.1f,%.1f) rot=%.1f' % (o[k][0][0], o[k][0][1], o[k][1]))
np.save('lk34b.npy', np.array([[k, *o[k][0], o[k][1]] for k in sorted(o)]))
