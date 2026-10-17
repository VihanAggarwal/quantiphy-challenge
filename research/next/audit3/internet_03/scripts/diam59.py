import cv2, numpy as np
def map_coordinates(img, yx, order=1, mode=None):
    ys, xs = yx
    return cv2.remap(img.astype(np.float32), xs.astype(np.float32).reshape(1,-1), ys.astype(np.float32).reshape(1,-1), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE).ravel()
r = np.load('t59b.npy')
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0059.mp4')
F = {}; i = 0
while True:
    ok, im = c.read()
    if not ok: break
    F[i] = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(float); i += 1
ii = r[:, 0].astype(int); cx = r[:, 1]; cy = r[:, 2]
out = []
for j in range(1, len(r) - 1):
    f = ii[j]
    v = np.array([cx[j + 1] - cx[j - 1], cy[j + 1] - cy[j - 1]]); v /= np.linalg.norm(v)
    p = np.array([-v[1], v[0]])
    s = np.arange(-110, 110.01, 0.5)
    prof = []
    for o in np.arange(-6, 6.1, 1.0):
        xs = cx[j] + s * p[0] + o * v[0]; ys = cy[j] + s * p[1] + o * v[1]
        prof.append(map_coordinates(F[f], [ys, xs], order=1, mode='nearest'))
    prof = np.mean(prof, 0)
    # also do several angles (perp only is blur-free). interior level: median of |s|<35 ; bg: median of |s| in 90..110
    inner = np.median(prof[np.abs(s) < 35]); bg = np.median(prof[np.abs(s) > 95])
    thr = (inner + bg) / 2
    inside = prof < thr
    # find crossing from center outward
    c0 = len(s) // 2
    k = c0
    while k < len(s) - 1 and inside[k]: k += 1
    rgt = s[k - 1] + (thr - prof[k - 1]) / (prof[k] - prof[k - 1]) * 0.5
    k = c0
    while k > 0 and inside[k]: k -= 1
    lft = s[k + 1] - (thr - prof[k + 1]) / (prof[k] - prof[k + 1]) * 0.5
    clip = (cy[j] - 70 < 0) or (cx[j] + 70 > 1919) or (cy[j] + 70 > 1079)
    out.append((f, rgt - lft))
    print(f, 'd_perp=%.1f inner=%.0f bg=%.0f %s' % (rgt - lft, inner, bg, 'CLIP' if clip else ''))
np.save('d59.npy', np.array(out))
