import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0066.mp4')
F = []
while True:
    ok, im = c.read()
    if not ok: break
    F.append(im)
lab = cv2.cvtColor(F[60], cv2.COLOR_BGR2LAB).astype(float)
print('ball L,a,b', lab[420:450, 1000:1040].reshape(-1, 3).mean(0), 'floor', lab[420:450, 1500:1540].reshape(-1, 3).mean(0), 'floor2', lab[700:730, 600:640].reshape(-1,3).mean(0))
sh = {}
ref = cv2.cvtColor(cv2.resize(F[40], (960, 540)), cv2.COLOR_BGR2GRAY).astype(np.float32); win = cv2.createHanningWindow((960, 540), cv2.CV_32F)
X = {}; Wd = {}
for i in range(50, 72):
    gi = cv2.cvtColor(cv2.resize(F[i], (960, 540)), cv2.COLOR_BGR2GRAY).astype(np.float32)
    (dx, dy), _ = cv2.phaseCorrelate(ref, gi, win); dx *= 2
    L = cv2.cvtColor(F[i], cv2.COLOR_BGR2LAB).astype(float)
    m = (L[..., 1] > 138) & (L[..., 0] < 85)
    band = m[380:500, :].mean(0) > 0.5
    idx = np.nonzero(band)[0]
    if len(idx) < 50: continue
    runs = np.split(idx, np.nonzero(np.diff(idx) > 5)[0] + 1); run = max(runs, key=len)
    X[i] = (run[0] + run[-1]) / 2 - dx; Wd[i] = run[-1] - run[0]
    print(i, 'L=%d R=%d mid=%.1f w=%d camdx=%.1f' % (run[0], run[-1], X[i], Wd[i], dx))
ii = np.array(sorted(X)); xx = np.array([X[k] for k in ii])
print('dx', np.round(np.diff(xx), 1))
np.save('x66.npy', np.c_[ii, xx])
