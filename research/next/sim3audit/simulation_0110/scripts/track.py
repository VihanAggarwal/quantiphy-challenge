"""Track both red cells in a clip: luma segmentation, per-frame bbox extents, centroid.
Usage: python track.py <video> <out.json>"""
import sys, json, cv2, numpy as np
vid, out = sys.argv[1], sys.argv[2]
cap = cv2.VideoCapture(vid)
res = []
i = 0
while True:
    ok, f = cap.read()
    if not ok: break
    Y = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(float)
    bg = np.median(Y[:50, :50])
    # cell darker than bg; threshold halfway between bg and typical cell luma
    cell = np.percentile(Y[Y < bg - 30], 50) if (Y < bg - 30).sum() > 100 else bg - 60
    thr = (bg + cell) / 2
    m = Y < thr
    m8 = m.astype(np.uint8)
    inv = (1 - m8).copy(); ff = inv.copy(); msk = np.zeros((m.shape[0]+2, m.shape[1]+2), np.uint8)
    cv2.floodFill(ff, msk, (0, 0), 2)
    m8 = np.where(ff == 1, 1, m8).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m8)
    sizes = stats[1:, cv2.CC_STAT_AREA]
    objs = []
    for k in np.argsort(sizes)[::-1][:2]:
        if sizes[k] < 200: continue
        ys, xs = np.where(lab == k + 1)
        # subpixel extents via alpha = clip((bg - Y)/(bg-cell)) summed along rows / cols
        y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
        sub = Y[max(y0-3,0):y1+4, max(x0-3,0):x1+4]
        a = np.clip((bg - sub) / (bg - cell), 0, 1)
        colsum = a.max(axis=0); rowsum = a.max(axis=1)
        w = colsum.sum(); h = rowsum.sum()
        # centroid weighted
        yy, xx = np.mgrid[max(y0-3,0):y1+4, max(x0-3,0):x1+4]
        cx = (a * xx).sum() / a.sum(); cy = (a * yy).sum() / a.sum()
        objs.append(dict(cx=float(cx), cy=float(cy), w=float(w), h=float(h), x0=int(x0), x1=int(x1), y0=int(y0), y1=int(y1),
                         bbcx=float((x0 + x1) / 2), bbcy=float((y0 + y1) / 2), area=float(a.sum())))
    objs.sort(key=lambda o: o['cx'])
    res.append(dict(frame=i, bg=float(bg), cell=float(cell), objs=objs))
    i += 1
json.dump(res, open(out, 'w'), indent=0)
print('frames', i)
