import cv2, numpy as np
r = np.load('t66.npy')
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0066.mp4')
F = []
while True:
    ok, im = c.read()
    if not ok: break
    F.append(im)
# ball: red-brown, use (R - B) chroma to separate from floor (floor is tan: R>G>B too...). use 'a' channel of LAB
ds = []; xs = {}
for row in r:
    i = int(row[0])
    if i < 53 or i > 68: continue
    lab = cv2.cvtColor(F[i], cv2.COLOR_BGR2LAB).astype(float)
    x, y = int(row[1]), int(row[2])
    # vertical profile of a-channel through centre band x +-15
    pa = lab[:, x - 15:x + 15, 1].mean(1)
    pL = lab[:, x - 15:x + 15, 0].mean(1)
    seg = pL[y - 200:y + 200]
    inner = np.median(seg[170:230]); bg = np.median(np.r_[seg[:30], seg[-30:]])
    thr = (inner + bg) / 2
    ins = seg < thr if inner < bg else seg > thr
    cc = 200; k = cc
    while k < 399 and ins[k]: k += 1
    bot = k - 1 + (thr - seg[k - 1]) / (seg[k] - seg[k - 1])
    k = cc
    while k > 0 and ins[k]: k -= 1
    top = k + 1 - (thr - seg[k + 1]) / (seg[k] - seg[k + 1])
    d = bot - top; ds.append(d)
    # horizontal centre: use L-channel row profile, midpoint of 50% crossings (blur symmetric)
    rp = lab[y - 30:y + 30, :, 0].mean(0)
    seg2 = rp[x - 260:x + 260]; inner2 = np.median(seg2[240:280]); bg2 = np.median(np.r_[seg2[:20], seg2[-20:]])
    thr2 = (inner2 + bg2) / 2; ins2 = seg2 < thr2
    k = 260
    while k < 519 and ins2[k]: k += 1
    R = k
    k = 260
    while k > 0 and ins2[k]: k -= 1
    Lft = k
    xs[i] = x - 260 + (R + Lft) / 2 - row[6]
    print(i, 'vert diam=%.1f (top %.1f bot %.1f)  xmid=%.1f  hwidth=%d' % (d, top + y - 200, bot + y - 200, xs[i], R - Lft))
D = np.median(ds); print('median vertical diam', D)
ii = np.array(sorted(xs)); X = np.array([xs[k] for k in ii])
print('dx per frame', np.round(np.diff(X), 1))
for f0 in (54, 57, 60, 63, 66):
    s = (ii >= f0 - 3) & (ii <= f0 + 3)
    p = np.polyfit(ii[s] / 30., X[s], 2)
    v = abs(np.polyval(np.polyder(p), f0 / 30.))
    print('t=%.1f v_px=%.0f px/s -> v=%.3f m/s (ball 24cm scale)' % (f0 / 30, v, v * 0.24 / D))
p = np.polyfit(ii / 30., X, 2)
for a, b in [(51, 54), (54, 57), (57, 60), (60, 63)]:
    print('disp %d-%d: %.3f m' % (a, b, abs(np.polyval(p, b / 30) - np.polyval(p, a / 30)) * 0.24 / D))
