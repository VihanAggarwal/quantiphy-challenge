import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0034.mp4')
F = []
while True:
    ok, im = c.read()
    if not ok: break
    F.append(cv2.resize(im, (1920, 1080), interpolation=cv2.INTER_AREA))
bg = F[0].astype(float)
# camera shake check: phase corr on top band (tiles), rows 0-350
g0 = cv2.cvtColor(F[0], cv2.COLOR_BGR2GRAY).astype(np.float32)[0:380, :]
win = cv2.createHanningWindow(g0.shape[::-1], cv2.CV_32F)
out = []
for i in range(5, 60):
    gi = cv2.cvtColor(F[i], cv2.COLOR_BGR2GRAY).astype(np.float32)[0:380, :]
    (dx, dy), _ = cv2.phaseCorrelate(g0, gi, win)
    d = np.abs(F[i].astype(float) - bg).sum(2)
    hsv = cv2.cvtColor(F[i], cv2.COLOR_BGR2HSV)
    m = (d > 40) & (hsv[..., 1] < 40)
    rowsel = []
    for (a, b) in [(540, 580), (580, 620)]:
        col = m[a:b, 700:1700].mean(0) > 0.5
        idx = np.nonzero(col)[0]
        if len(idx) < 50: rowsel.append((np.nan, np.nan)); continue
        # largest run
        runs = np.split(idx, np.nonzero(np.diff(idx) > 3)[0] + 1)
        run = max(runs, key=len)
        rowsel.append((run[0] + 700, run[-1] + 700))
    # vertical extent at column band around center of first band
    out.append((i, dx, dy, *rowsel[0], *rowsel[1]))
    print(i, 'shift=(%.1f,%.1f)' % (dx, dy), 'band540-580 L=%s R=%s' % rowsel[0], 'band580-620 L=%s R=%s' % rowsel[1])
np.save('t34.npy', np.array(out, dtype=float))
