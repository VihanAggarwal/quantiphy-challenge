import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0066.mp4')
F = []
while True:
    ok, im = c.read()
    if not ok: break
    F.append(im)
print(len(F))
# camera motion: phase correlation on whole frame (downscaled) vs frame 40
def gs(i): return cv2.cvtColor(cv2.resize(F[i], (960, 540)), cv2.COLOR_BGR2GRAY).astype(np.float32)
ref = gs(40); win = cv2.createHanningWindow((960, 540), cv2.CV_32F)
sh = {}
for i in range(0, len(F)):
    (dx, dy), rr = cv2.phaseCorrelate(ref, gs(i), win); sh[i] = (2 * dx, 2 * dy)
print('shifts', {i: (round(sh[i][0], 1), round(sh[i][1], 1)) for i in range(0, 100, 5)})
# background: median of frames 30-45 and 80-95 aligned? use frame 40 and 90 shift-aligned
bgs = []
for b in (35, 40, 45, 85, 90):
    M = np.float32([[1, 0, sh[40][0] - sh[b][0] + 0], [0, 1, sh[40][1] - sh[b][1]]])
    bgs.append(cv2.warpAffine(F[b], M, (1920, 1080), borderMode=cv2.BORDER_REPLICATE).astype(int))
bg40 = np.median(np.array(bgs), 0)
res = []
for i in range(46, 76):
    M = np.float32([[1, 0, sh[i][0] - sh[40][0]], [0, 1, sh[i][1] - sh[40][1]]])
    bg = cv2.warpAffine(bg40.astype(np.float32), M, (1920, 1080), borderMode=cv2.BORDER_REPLICATE)
    d = np.abs(F[i].astype(float) - bg).sum(2)
    m = (d > 60).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n < 2: print(i, 'none'); continue
    k = 1 + np.argmax(st[1:, 4]); x, y, w, h, a = st[k]
    edge = x <= 0 or x + w >= 1920 or y <= 0 or y + h >= 1080
    res.append((i, cen[k][0], cen[k][1], w, h, a, sh[i][0], sh[i][1], edge))
    print(i, 'c=(%.0f,%.0f) w=%d h=%d area_eq=%.0f shift=(%.1f,%.1f) %s' % (cen[k][0], cen[k][1], w, h, 2 * np.sqrt(a / np.pi), sh[i][0], sh[i][1], 'EDGE' if edge else ''))
np.save('t66.npy', np.array(res, dtype=float))
