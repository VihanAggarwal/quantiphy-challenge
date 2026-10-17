# simulation_0195: Callisto diameter from edge coverage (sum of normalized intensity over the disk / pi -> radius), f=2667 from orbit check.
import cv2, numpy as np
cap = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0195.mp4')
tr = np.load('/home/user/quantiphy-challenge/research/next/sim3audit/group5/callisto_track.npy')
fr = []
while True:
    ok, f = cap.read()
    if not ok: break
    fr.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32))
F = 2667.0; c = np.array([960., 540.]); J = np.array([940.4, 489.06])
def ray(p):
    d = np.array([p[0] - c[0], p[1] - c[1], F]); return d / np.linalg.norm(d)
out = []
for row in tr[::5]:
    i = int(row[0]); x, y = row[1], row[2]
    g = fr[i]; xi, yi = int(round(x)), int(round(y))
    sub = g[yi - 30:yi + 31, xi - 30:xi + 31]
    yy, xx = np.mgrid[-30:31, -30:31] + 0.0
    rr = np.hypot(xx - (x - xi), yy - (y - yi))
    bgv = np.median(sub[rr > 22]); inner = np.median(sub[rr < 8]) - bgv
    cov = np.clip((sub - bgv) / inner, 0, 1.3)
    A = cov[rr < 20].sum(); d_cov = 2 * np.sqrt(A / np.pi)
    # half-max radius from radial profile
    prof = [np.mean(sub[(rr >= r - 0.5) & (rr < r + 0.5)]) - bgv for r in np.arange(0, 22)]
    prof = np.array(prof) / inner
    k = np.argmax(prof < 0.5); rh = k - 1 + (prof[k - 1] - 0.5) / (prof[k - 1] - prof[k])
    # range at frame i: interpolate along the fitted orbit -> approximate linear interpolation between 13.004 (t=0) and 13.856 (t=3)
    out.append((i, d_cov, 2 * rh))
out = np.array(out)
t = out[:, 0] / 30.0
# range model: circle about J (R=4.26) -> use linear interp as approximation (orbit arc small)
rng = 13.004 + (13.856 - 13.004) * t / 3.0
for (i, dc, dh), r in zip(out, rng):
    pass
Dc = out[:, 1] * rng / F; Dh = out[:, 2] * rng / F
print('frames', out[:, 0].astype(int))
print('cov diam px', np.round(out[:, 1], 2)); print('halfmax diam px', np.round(out[:, 2], 2))
print('D (coverage) mean %.4f  D (half-max) mean %.4f' % (Dc.mean(), Dh.mean()))
print('Jupiter D from 282-283 px at 16.549: %.3f-%.3f' % (2 * 16.549 * np.sin(np.arctan(141.0 / F)), 2 * 16.549 * np.sin(np.arctan(141.5 / F))))
