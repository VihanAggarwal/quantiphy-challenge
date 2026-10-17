import cv2, numpy as np, sys
# usage: bgobj.py video bgframe th [ymin ymax] -> per-frame components
v = sys.argv[1]; bgf = int(sys.argv[2]); th = float(sys.argv[3])
ylim = tuple(map(int, sys.argv[4:6])) if len(sys.argv) > 5 else None
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4' % v)
fr = []
while True:
    ok, im = c.read()
    if not ok: break
    fr.append(im.astype(np.float32))
bg = fr[bgf] if bgf >= 0 else np.median(np.stack(fr), axis=0)
for i, im in enumerate(fr):
    d = np.abs(im - bg).max(axis=2)
    m = (d > th).astype(np.uint8)
    if ylim: m[:ylim[0]] = 0; m[ylim[1]:] = 0
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    out = ['x%d-%d(%d) y%d-%d(%d) a%d c%.1f,%.1f' % (s[0], s[0]+s[2], s[2], s[1], s[1]+s[3], s[3], s[4], ce[0], ce[1]) for s, ce in zip(st[1:], cen[1:]) if s[4] > 200]
    print(i, ' | '.join(out))
