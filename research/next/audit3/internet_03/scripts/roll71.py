import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0071.mp4')
F = []
while True:
    ok, im = c.read()
    if not ok: break
    F.append(cv2.resize(im, (1920, 1080), interpolation=cv2.INTER_AREA))
for fr in (30, 52, 58):
    g = cv2.cvtColor(F[fr], cv2.COLOR_BGR2GRAY).astype(float)
    cxr = {30: 1200, 52: 975, 58: 957}[fr]
    colp = g[380:1000, cxr - 70:cxr - 20].mean(1)
    d = np.diff(cv2.GaussianBlur(colp.reshape(-1, 1), (1, 5), 0).ravel())
    # top edge: biggest positive/negative change in y 450-600, bottom edge y 800-950
    top = 380 + 450 - 380 + np.argmax(np.abs(d[450 - 380:620 - 380]))
    bot = 380 + 780 - 380 + np.argmax(np.abs(d[780 - 380:950 - 380]))
    rowp = g[560:640, :].mean(0)
    dr = np.diff(cv2.GaussianBlur(rowp.reshape(1, -1), (5, 1), 0).ravel())
    L = cxr - 260 + np.argmax(np.abs(dr[cxr - 260:cxr - 80])); R = cxr + 80 + np.argmax(np.abs(dr[cxr + 80:cxr + 260]))
    print(fr, 'top=%d bot=%d H=%d   L=%d R=%d W=%d  ratio H/W=%.3f -> diam=%.2f cm' % (top, bot, bot - top, L, R, R - L, (bot - top) / (R - L), 10 * (bot - top) / (R - L)))
