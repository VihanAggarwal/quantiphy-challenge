import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0177_segmented.mp4')
i = 0; R = []
while True:
    ok, im = c.read()
    if not ok: break
    d = 255 - im.astype(np.float32).min(axis=2)
    m = (d > 40).astype(np.uint8)
    ys, xs = np.nonzero(m)
    # body column profile: per-column top
    R.append((i, xs.mean(), ys.mean(), xs.min(), xs.max(), ys.min(), ys.max(), len(xs)))
    if i % 6 == 0 or i == 59: print('%d c%.1f,%.1f x%d-%d(%d) y%d-%d(%d) n%d' % (i, xs.mean(), ys.mean(), xs.min(), xs.max(), xs.max()-xs.min(), ys.min(), ys.max(), ys.max()-ys.min(), len(xs)))
    i += 1
R = np.array(R)
p = np.polyfit(R[:, 0], R[:, 1], 1); print('centroid vx px/frame', p[0], 'x0-59', R[-1,1]-R[0,1])
p = np.polyfit(R[:, 0], R[:, 3], 1); print('left edge vx', p[0]); p = np.polyfit(R[:, 0], (R[:, 3]+R[:,4])/2, 1); print('bbox centre vx', p[0])
print('median height', np.median(R[:, 6]-R[:, 5]), 'median top', np.median(R[:,5]), 'median bottom', np.median(R[:,6]))
