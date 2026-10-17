import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0071.mp4')
ok, im = c.read()
g = cv2.cvtColor(cv2.resize(im, (1920, 1080), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(float)
def minima(p, off, k=8, sep=40, thr=12):
    base = cv2.blur(p.reshape(1, -1).astype(np.float32), (101, 1)).ravel()
    dip = base - p
    out = []
    for i in np.argsort(-dip):
        if dip[i] < thr: break
        if all(abs(i - j) > sep for j in out): out.append(i)
        if len(out) >= k: break
    return sorted(int(o + off) for o in out)
# horizontal grout rows: row profile in column band without holder (x 1350-1900)
print('rows (x1350-1900):', minima(g[:, 1350:1900].mean(1), 0))
print('rows (x0-450):', minima(g[:, 0:450].mean(1), 0))
# vertical grouts: within tile row band y 360-860 (middle course) and top course y 0-320, bottom y 900-1080
print('cols middle course y380-500:', minima(g[380:500, :].mean(0), 0))
print('cols top course y40-300:', minima(g[40:300, :].mean(0), 0))
print('cols bottom course y900-1070:', minima(g[900:1070, :].mean(0), 0))
