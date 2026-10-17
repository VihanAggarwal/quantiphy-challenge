# Radial outer-edge half-max crossings of HSV saturation (or gray diff) around ball centroid; circle fit -> diameter.
import cv2, numpy as np, sys, json
vid, trk, chan = sys.argv[1], sys.argv[2], sys.argv[3]
rmax = float(sys.argv[4]) if len(sys.argv) > 4 else 30
tr = dict((i, r) for i, r in json.load(open(trk)))
c = cv2.VideoCapture(vid); i = -1; out = []
angs = np.deg2rad(np.arange(0, 360, 5))
while True:
    ok, f = c.read(); i += 1
    if not ok: break
    r = tr.get(i)
    if r is None or r['cx'] < rmax + 5 or r['cx'] > f.shape[1] - rmax - 5 or r['cy'] < rmax + 5 or r['cy'] > f.shape[0] - rmax - 5: continue
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV).astype(np.float32)
    img = hsv[..., 1] if chan == 'sat' else (255 - cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32))
    cx, cy = r['cx'], r['cy']
    for it in range(2):
        rr = np.arange(0, rmax, 0.25)
        P = []
        for a in angs:
            xs = (cx + rr * np.cos(a)).astype(np.float32); ys = (cy + rr * np.sin(a)).astype(np.float32)
            pr = cv2.remap(img, xs.reshape(1, -1), ys.reshape(1, -1), cv2.INTER_LINEAR)[0]
            bgv = np.median(pr[-12:]); inn = np.percentile(pr[:int(len(rr) * 0.4)], 75)
            th = (bgv + inn) / 2
            above = np.nonzero(pr > th)[0]
            if len(above) == 0: continue
            k = above[-1]
            if k + 1 >= len(pr): continue
            t = rr[k] + 0.25 * (pr[k] - th) / max(pr[k] - pr[k + 1], 1e-6)
            P.append((cx + t * np.cos(a), cy + t * np.sin(a), a))
        P = np.array(P)
        # algebraic circle fit
        A = np.c_[2 * P[:, 0], 2 * P[:, 1], np.ones(len(P))]; b = P[:, 0] ** 2 + P[:, 1] ** 2
        sol = np.linalg.lstsq(A, b, rcond=None)[0]; cx, cy = sol[0], sol[1]; R = np.sqrt(sol[2] + cx ** 2 + cy ** 2)
    rad = np.hypot(P[:, 0] - cx, P[:, 1] - cy)
    # also report horizontal and vertical radii (angles near 0/180 and 90/270)
    ang = np.rad2deg(P[:, 2]) % 360
    h = np.median(rad[(np.abs(ang - 0) < 20) | (np.abs(ang - 180) < 20) | (ang > 340)]); v = np.median(rad[(np.abs(ang - 90) < 20) | (np.abs(ang - 270) < 20)])
    vb = np.median(rad[np.abs(ang - 90) < 20]); vt = np.median(rad[np.abs(ang - 270) < 20])
    out.append((i, 2 * R, 2 * h, 2 * v, vt, vb, cx, cy))
    print(i, 'D_fit %.2f  D_h %.2f  D_v %.2f (top r %.2f bottom r %.2f) c=(%.1f,%.1f)' % (2 * R, 2 * h, 2 * v, vt, vb, cx, cy))
o = np.array([x[1:4] for x in out])
print('median D_fit %.2f D_h %.2f D_v %.2f' % tuple(np.median(o, axis=0)))
