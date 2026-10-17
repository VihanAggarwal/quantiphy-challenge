import cv2, numpy as np, sys, json
vid = sys.argv[1]
c = cv2.VideoCapture(vid)
frames = []
while True:
    ok, f = c.read()
    if not ok: break
    frames.append(f)
f0 = frames[0].astype(np.int16)
u = np.array([1080., 1000.]); u /= np.linalg.norm(u); nrm = np.array([-u[1], u[0]])
res = []
for i, f in enumerate(frames):
    d = np.abs(f.astype(np.int16) - f0).sum(2)
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    m = ((d > 40) & (hsv[..., 1] > 70)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    nl, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if nl < 2: print(i, 'none'); res.append(None); continue
    k = 1 + np.argmax(st[1:, 4])
    ys, xs = np.nonzero(lab == k)
    s = xs * u[0] + ys * u[1]; t = xs * nrm[0] + ys * nrm[1]
    r = dict(cx=float(xs.mean()), cy=float(ys.mean()), smin=float(s.min()), smax=float(s.max()), sc=float(s.mean()), tmin=float(t.min()), tmax=float(t.max()), area=int(len(xs)), x0=int(xs.min()), x1=int(xs.max()), y0=int(ys.min()), y1=int(ys.max()))
    res.append(r)
    print(i, 'c=(%.1f,%.1f) s=[%.1f %.1f] sc=%.1f slen=%.1f tlen=%.1f area=%d bbox x%d-%d y%d-%d' % (r['cx'], r['cy'], r['smin'], r['smax'], r['sc'], r['smax']-r['smin'], r['tmax']-r['tmin'], r['area'], r['x0'], r['x1'], r['y0'], r['y1']))
json.dump(res, open(sys.argv[2], 'w'))
