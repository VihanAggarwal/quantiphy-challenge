import cv2, numpy as np
img = cv2.imread('g_0014x_00.png').astype(float)
# table mask: brownish: R > B + 25 and not white
B,G,R = img[...,0], img[...,1], img[...,2]
tab = (R - B > 25) & (R < 235)
def subpix_boundary(vals, i):
    return i
def fit_line(pts):
    pts = np.array(pts, float)
    vx, vy, x0, y0 = cv2.fitLine(pts.astype(np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
    n = np.array([-vy, vx]); c = -n @ np.array([x0, y0])
    r = pts @ n + c
    return np.array([n[0], n[1], c]), r
# left edge: for rows, first table pixel from left in x range 380..560
L = []
for y in list(range(345, 432)) + list(range(458, 495)):
    xs = np.where(tab[y, 380:560])[0]
    if len(xs): L.append((380 + xs[0] - 0.5, y))
R_ = []
for y in range(318, 452):
    xs = np.where(tab[y, 600:800])[0]
    if len(xs): R_.append((600 + xs[-1] + 0.5, y))
# back edge: for columns, first table pixel from top
Bk = []
for x in list(range(605, 652)):
    ys = np.where(tab[280:400, x])[0]
    if len(ys): Bk.append((x, 280 + ys[0] - 0.5))
lL, rL = fit_line(L); lR, rR = fit_line(R_); lB, rB = fit_line(Bk)
print('left rms', rL.std(), 'right rms', rR.std(), 'back rms', rB.std(), len(Bk))
# front edge: top surface -> front face transition; use luminance drop in columns
gray = img.mean(2)
F = []
for x in range(435, 720, 3):
    col = gray[400:520, x]
    d = col[2:] - col[:-2]
    i = np.argmin(d) + 1
    F.append((x, 400 + i))
lF, rF = fit_line(F)
print('front rms', rF.std())
np.save('t14_lines.npy', np.array([lL, lR, lB, lF]))
def inter(a, b):
    p = np.cross(a, b); return p[:2] / p[2]
BL = inter(lL, lB); BR = inter(lR, lB); FR = inter(lR, lF); FL = inter(lL, lF)
print('corners BL', BL, 'BR', BR, 'FR', FR, 'FL', FL)
np.save('t14_corners.npy', np.array([BL, BR, FR, FL]))
print('--- refined front edge')
F = []
for x in range(432, 726, 2):
    yexp = 499 - 0.136 * (x - 427)
    y0 = int(yexp - 8)
    col = gray[y0:y0 + 17, x]
    d = col[2:] - col[:-2]
    i = np.argmin(d) + 1
    F.append((x, y0 + i))
F = np.array(F, float)
lF, rF = fit_line(F)
keep = np.abs(rF) < 2.5
lF, rF = fit_line(F[keep])
print('front rms', rF.std(), keep.sum(), len(F))
BL = inter(lL, lB); BR = inter(lR, lB); FR = inter(lR, lF); FL = inter(lL, lF)
print('corners BL', BL, 'BR', BR, 'FR', FR, 'FL', FL)
np.save('t14_corners.npy', np.array([BL, BR, FR, FL]))
np.save('t14_lines.npy', np.array([lL, lR, lB, lF]))
vis = img.astype(np.uint8).copy()
for P in [BL, BR, FR, FL]:
    cv2.circle(vis, tuple(int(round(v)) for v in P), 3, (0, 0, 255), -1)
cv2.polylines(vis, [np.array([BL, BR, FR, FL]).astype(np.int32)], True, (255, 0, 0), 1)
cv2.imwrite('t14_vis.png', cv2.resize(vis[270:560, 380:800], None, fx=2.5, fy=2.5, interpolation=cv2.INTER_NEAREST))
