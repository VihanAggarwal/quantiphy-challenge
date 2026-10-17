import cv2, numpy as np, json
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0040x.mp4')
fr = []
while True:
    ok, f = c.read()
    if not ok: break
    fr.append(f)
im = np.median(np.array(fr[5:20]).astype(np.float32), axis=0)
g = im.mean(2)
mask = g > 25
H, W = g.shape
def topedge(x0, x1, ymin=400, ymax=620):
    pts = []
    for x in range(x0, x1):
        col = mask[ymin:ymax, x]
        idx = np.nonzero(col)[0]
        if len(idx): 
            y = ymin + idx[0]
            # subpixel: interpolate threshold crossing
            a, b = g[y-1, x], g[y, x]
            yy = y - 1 + (25 - a) / (b - a) if b != a else y
            pts.append((x, yy))
    return np.array(pts)
def fitline(p):
    vx, vy, x0, y0 = cv2.fitLine(p.astype(np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
    n = np.array([-vy, vx]); d = n @ [x0, y0]
    r = p @ n - d
    return np.array([n[0], n[1], -d]), np.abs(r).max(), np.sqrt((r**2).mean())
left = topedge(225, 430)
back = np.vstack([topedge(462, 478), topedge(820, 905)])
right = topedge(935, 1125)
# front edge: strongest negative-going brightness transition (light top -> dark front face) per column
fp = []
for x in list(range(225, 500)) + list(range(640, 1125)):
    yp = int(536 + (x - 207) * (586.5 - 536) / (1141 - 207))
    col = g[yp-10:yp+10, x]
    dg = np.diff(col)
    i = np.argmin(dg)  # largest drop
    # subpixel parabola
    if 0 < i < len(dg)-1:
        a,b,cc = dg[i-1],dg[i],dg[i+1]; off = 0.5*(a-cc)/(a-2*b+cc)
    else: off = 0
    fp.append((x, yp-10 + i + 0.5 + off))
front = np.array(fp)
L = {}
for name, p in [('left', left), ('back', back), ('right', right), ('front', front)]:
    l, mx, rms = fitline(p)
    L[name] = l
    print(name, len(p), 'max res %.2f rms %.2f' % (mx, rms))
def X(a, b):
    p = np.cross(L[a], L[b]); return p[:2] / p[2]
corners = dict(fl=X('front', 'left'), fr=X('front', 'right'), br=X('back', 'right'), bl=X('back', 'left'))
for k, v in corners.items(): print(k, v.round(2))
json.dump({k: v.tolist() for k, v in corners.items()}, open('/home/user/quantiphy-challenge/research/next/labaudit2/0040/remeasure_b/table_corners.json', 'w'))
