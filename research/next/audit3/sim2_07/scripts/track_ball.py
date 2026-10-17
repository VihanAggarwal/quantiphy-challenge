import cv2, numpy as np, sys, json
vid = sys.argv[1]; mode = sys.argv[2]  # 'seg' or 'bg'
c = cv2.VideoCapture(vid)
frames = []
while True:
    ok, f = c.read()
    if not ok: break
    frames.append(f)
n = len(frames)
if mode == 'bg':
    # background = per-pixel median over a strided subset (computed on the fly, not saved)
    idx = list(range(0, n, 3))
    bg = np.median(np.stack([frames[i] for i in idx]).astype(np.int16), axis=0).astype(np.int16)
out = []
for i, f in enumerate(frames):
    fi = f.astype(np.int16)
    if mode == 'seg':
        d = (765 - fi.sum(2)).astype(np.float32)
    else:
        d = np.abs(fi - bg).sum(2).astype(np.float32)
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    m = (d > 60)
    if mode == 'bg':
        m &= (hsv[..., 1] > 60)
    m = m.astype(np.uint8)
    nl, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if nl < 2:
        out.append((i, None)); continue
    k = 1 + np.argmax(st[1:, 4])
    x, y, w, h, a = st[k]
    if a < 30:
        out.append((i, None)); continue
    mk = lab == k
    ys, xs = np.nonzero(mk)
    out.append((i, dict(cx=float(xs.mean()), cy=float(ys.mean()), w=int(w), h=int(h), area=int(a), eqd=float(2*np.sqrt(a/np.pi)), x0=int(x), y0=int(y))))
for i, r in out:
    if r is None: print(i, 'none')
    else: print(i, '%.2f %.2f w=%d h=%d area=%d eqd=%.2f x0=%d y0=%d' % (r['cx'], r['cy'], r['w'], r['h'], r['area'], r['eqd'], r['x0'], r['y0']))
json.dump([[i, r] for i, r in out], open(sys.argv[3], 'w'))
