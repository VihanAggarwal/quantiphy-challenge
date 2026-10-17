import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0059.mp4')
for fr in (0, 20, 40, 60, 78, 100):
    c.set(cv2.CAP_PROP_POS_FRAMES, fr); ok, im = c.read()
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(float)
    sub = g[960:1080, 820:980]
    # plate is brighter than wall; find plate bbox by threshold midway
    wall = np.median(sub)
    # find plate core: brightest region
    hi = np.percentile(sub, 99)
    thr = (wall + hi) / 2
    m = (sub > thr).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    k = 1 + np.argmax(st[1:, 4])
    x, y, w, h, a = st[k]
    # refine by subpixel profiles: column profile through middle rows, row profile through middle columns
    cy, cx = int(cen[k][1]), int(cen[k][0])
    rows = sub[cy - 8:cy + 8, :].mean(0)
    cols = sub[:, cx - 6:cx + 6].mean(1)
    def width(p, thr):
        idx = np.nonzero(p > thr)[0]
        # subpixel crossing
        i0, i1 = idx.min(), idx.max()
        l = i0 - 1 + (thr - p[i0 - 1]) / (p[i0] - p[i0 - 1])
        r = i1 + (p[i1] - thr) / (p[i1] - p[i1 + 1])
        return r - l, l, r
    wd = width(rows, (np.median(rows) + rows[cx - 820 + 0 if False else cx].max() if False else (np.median(rows) + np.percentile(rows, 95)) / 2))
    hd = width(cols, (np.median(cols) + np.percentile(cols, 90)) / 2)
    print(fr, 'thr bbox w=%d h=%d' % (w, h), 'profile w=%.1f (%.1f-%.1f) h=%.1f (%.1f-%.1f)' % (wd[0], wd[1] + 820, wd[2] + 820, hd[0], hd[1] + 960, hd[2] + 960))
