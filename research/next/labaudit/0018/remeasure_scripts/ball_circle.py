import numpy as np, cv2
fr = np.load('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/fr0018.npy').astype(np.float32)
avg = fr[0:11].mean(0)
g = cv2.cvtColor(avg.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(float)
cx0, cy0 = 542, 263
pts = []
for ang in np.arange(-150, 91, 5):  # degrees; skip the lower-left where the hand is (approx 100..210 deg in image coords)
    a = np.deg2rad(ang)
    dx, dy = np.cos(a), np.sin(a)
    rs = np.arange(10, 35, 0.25)
    xs = cx0 + rs*dx; ys = cy0 + rs*dy
    prof = cv2.remap(g.astype(np.float32), xs.astype(np.float32).reshape(1, -1), ys.astype(np.float32).reshape(1, -1), cv2.INTER_LINEAR).ravel()
    bg = np.median(prof[-12:])
    # ball outer boundary: last radius where profile is well above background (white panels) -> use max gradient from outside
    grad = -np.gradient(prof)
    k = np.argmax(grad[20:]) + 20
    pts.append((xs[k], ys[k], ang, rs[k], bg))
P = np.array(pts)
# algebraic circle fit
x, y = P[:, 0], P[:, 1]
A = np.vstack([x, y, np.ones_like(x)]).T; b = -(x**2 + y**2)
c = np.linalg.lstsq(A, b, rcond=None)[0]
xc, yc = -c[0]/2, -c[1]/2; R = np.sqrt(xc**2 + yc**2 - c[2])
res = np.sqrt((x-xc)**2 + (y-yc)**2) - R
keep = np.abs(res) < 2
A2 = A[keep]; b2 = b[keep]
c = np.linalg.lstsq(A2, b2, rcond=None)[0]
xc, yc = -c[0]/2, -c[1]/2; R = np.sqrt(xc**2 + yc**2 - c[2])
print('ball circle centre (%.1f, %.1f) radius %.2f px  diameter %.2f px  (used %d/%d pts)' % (xc, yc, R, 2*R, keep.sum(), len(keep)))
for p, r in zip(P, res): print('ang %4d r %.2f res %.2f' % (p[2], p[3], r))
