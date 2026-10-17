"""Table-top edges and corners (captured_0031). Edges from the x-render mask (median of frames 44-48, table
static) for the back/left/right edges, and from the o render (median frames 44-48) for the front crease
(top surface -> front face).  Lines fitted with RANSAC-ish trimming; corners = intersections.
"""
import cv2, numpy as np, json

def load(v):
    cap = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4'); fr = []
    while True:
        ok, f = cap.read()
        if not ok: break
        fr.append(f)
    return fr

fx = load('captured_0031x'); fo = load('captured_0031')
mx = np.median(np.stack([f.astype(np.float32) for f in fx[0:12]]), 0)
mo = np.median(np.stack([f.astype(np.float32) for f in fo[0:12]]), 0)
mask = (mx.max(2) > 40).astype(np.float32)
mask = cv2.GaussianBlur(mask, (0, 0), 1.0)


def fitline(P):
    P = np.asarray(P, float)
    keep = np.ones(len(P), bool)
    for _ in range(5):
        c = P[keep].mean(0); u, s, vt = np.linalg.svd(P[keep] - c); d = vt[0]; n = np.array([-d[1], d[0]])
        res = (P - c) @ n
        keep = np.abs(res) < max(0.4, 2.5 * np.std(res[keep]))
    c = P[keep].mean(0); u, s, vt = np.linalg.svd(P[keep] - c); d = vt[0]; n = np.array([-d[1], d[0]])
    return c, d, n, float(np.std((P[keep] - c) @ n)), int(keep.sum())


def sub(prof, lo):
    """sub-pixel location of the 0.5 crossing of a rising profile"""
    idx = np.nonzero((prof[:-1] < 0.5) & (prof[1:] >= 0.5))[0]
    if len(idx) == 0: return None
    k = idx[0]
    return lo + k + (0.5 - prof[k]) / (prof[k + 1] - prof[k])

# back edge: columns, scan down for mask 0->1 in y 405..440 (exclude columns where balls/hands interfere)
back = []
for x in list(range(585, 640)) + list(range(790, 840)):
    prof = mask[405:445, x]; y = sub(prof, 405)
    if y is not None: back.append((x, y))
# left edge: rows 430..478 scan right for 0->1 between x 450..600
left = []
for y in range(432, 478):
    prof = mask[y, 450:600]; x = sub(prof, 450)
    if x is not None: left.append((x, y))
right = []
for y in range(432, 490):
    prof = mask[y, 850:990][::-1]; x = sub(prof, 0)
    if x is not None: right.append((989 - x, y))
# front crease on o render: top surface brighter than front face? use vertical gradient of luminance
lum = cv2.GaussianBlur(mo.mean(2), (0, 0), 1.0)
gy = np.diff(lum, axis=0)
crease = []
for x in range(480, 950, 2):
    seg = gy[465:505, x]
    k = np.argmin(seg)  # bright (top) -> darker (front face) going down
    if k <= 0 or k >= len(seg) - 1: continue
    a, b, c = seg[k - 1], seg[k], seg[k + 1]
    off = 0.5 * (a - c) / (a - 2 * b + c + 1e-9)
    crease.append((x, 465 + k + off + 0.5))
L = {}
for name, P in [('back', back), ('left', left), ('right', right), ('crease', crease)]:
    c, d, n, sd, nk = fitline(P)
    L[name] = (c, d, n)
    print(name, 'n_pts', len(P), 'kept', nk, 'resid sd %.2f' % sd, 'centre', c.round(1), 'dir', d.round(4))


def inter(a, b):
    c1, d1, _ = L[a]; c2, d2, _ = L[b]
    A = np.c_[d1, -d2]; t = np.linalg.solve(A, c2 - c1)
    return c1 + t[0] * d1

C = {'BL': inter('back', 'left'), 'BR': inter('back', 'right'), 'FL': inter('crease', 'left'), 'FR': inter('crease', 'right')}
for k, v in C.items(): print(k, v.round(2))
json.dump({k: v.tolist() for k, v in C.items()}, open('/home/user/quantiphy-challenge/research/next/labaudit2/0031/corners.json', 'w'))
