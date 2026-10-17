import cv2, numpy as np, json, sys
V = sys.argv[1] if len(sys.argv) > 1 else 'captured_0040'
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4' % V)
fr = []
while True:
    ok, f = c.read()
    if not ok: break
    fr.append(f)
fr = np.array(fr)
bg = np.median(fr[28:49].astype(np.float32), axis=0)
out = {}
for k in range(26, 49):
    d = np.abs(fr[k].astype(np.float32) - bg).max(axis=2)
    # ball is bright: also require brightness
    gray = fr[k].astype(np.float32).mean(axis=2)
    m = ((d > 35) & (gray > 120)).astype(np.uint8)
    m[:, :330] = 0  # exclude thrower region
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n < 2:
        print(k, 'none'); continue
    i = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    ys, xs = np.nonzero(lab == i)
    pts = np.stack([xs, ys], 1).astype(np.float64)
    mu = pts.mean(0)
    cov = np.cov((pts - mu).T)
    ev, evec = np.linalg.eigh(cov)
    # extent along principal axes
    proj = (pts - mu) @ evec
    ext = proj.max(0) - proj.min(0) + 1
    out[k] = dict(cx=mu[0], cy=mu[1], area=int(st[i, cv2.CC_STAT_AREA]), bbox=[int(v) for v in st[i, :4]],
                  minor=float(ext[0]), major=float(ext[1]), ang=float(np.degrees(np.arctan2(evec[1, 1], evec[0, 1]))))
    print(k, '%.1f %.1f area %d bbox %s minor %.1f major %.1f ang %.0f' % (mu[0], mu[1], out[k]['area'], out[k]['bbox'], ext[0], ext[1], out[k]['ang']))
json.dump(out, open('/home/user/quantiphy-challenge/research/next/labaudit2/0040/remeasure_b/track_%s.json' % V, 'w'), indent=1)
