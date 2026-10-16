import cv2, numpy as np
def fit_line(pts):
    pts = np.asarray(pts, np.float32)
    vx, vy, x0, y0 = cv2.fitLine(pts, cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
    n = np.array([-vy, vx]); c = -n @ np.array([x0, y0]); return np.array([n[0], n[1], c])
def inter(a, b):
    p = np.cross(a, b); return p[:2] / p[2]
def board(fr, tag='0023x'):
    img = cv2.imread('f_%s_%02d.png' % (tag, fr)).astype(float)
    g = img.mean(2)
    white = g > 200
    L, R, T, Bt = [], [], [], []
    for y in range(392, 470):   # below book
        row = g[y]
        xs = np.where(row[460:720] > 200)[0]
        if len(xs) == 0: continue
        xl = 460 + xs[0]; xr = 460 + xs[-1]
        # subpixel at threshold midway between white (~250) and neighbour
        def sp(x0, x1):
            a, b = row[x0], row[x1]; th = 0.5 * (250 + min(a, b) if False else 0.5 * (row[x1] + row[x0]))
            return None
        lev_out_l = np.median(row[xl - 8:xl - 3]); th = 0.5 * (248 + lev_out_l)
        for xx in range(xl - 3, xl + 3):
            if row[xx] < th <= row[xx + 1]:
                L.append((xx + (th - row[xx]) / (row[xx + 1] - row[xx]), y)); break
        lev_out_r = np.median(row[xr + 3:xr + 8]); th = 0.5 * (248 + lev_out_r)
        for xx in range(xr + 3, xr - 3, -1):
            if row[xx] < th <= row[xx - 1]:
                R.append((xx - (th - row[xx]) / (row[xx - 1] - row[xx]), y)); break
    for x in range(560, 620):
        col = g[470:500, x]
        # bottom edge: white -> darker (table or edge)
        d = col[1:] - col[:-1]; i = np.argmin(d)
        a = -d; off = 0.5 * (a[i - 1] - a[i + 1]) / (a[i - 1] - 2 * a[i] + a[i + 1]) if 0 < i < len(a) - 1 else 0
        Bt.append((x, 470 + i + 0.5 + off))
    for x in list(range(525, 655)):
        col = g[340:380, x]
        d = col[1:] - col[:-1]; i = np.argmax(d)
        off = 0.5 * (d[i - 1] - d[i + 1]) / (d[i - 1] - 2 * d[i] + d[i + 1]) if 0 < i < len(d) - 1 else 0
        T.append((x, 340 + i + 0.5 + off))
    return [np.array(v) for v in (L, R, T, Bt)]
for fr in [0, 10, 20, 44, 48]:
    L, R, T, Bt = board(fr)
    lL, lR, lB = fit_line(L), fit_line(R), fit_line(Bt)
    rl = L @ lL[:2] + lL[2]; rr = R @ lR[:2] + lR[2]
    s = 'fr %d  L: x=%.4fy%+.1f rms %.2f | R: x=%.4fy%+.1f rms %.2f | bottom y@590 %.2f slope %.4f' % (
        fr, -lL[1] / lL[0], -lL[2] / lL[0], rl.std(), -lR[1] / lR[0], -lR[2] / lR[0], rr.std(), -(lB[0] * 590 + lB[2]) / lB[1], -lB[0] / lB[1])
    if fr >= 44:
        lT = fit_line(T); rt = T @ lT[:2] + lT[2]
        s += ' | top y@590 %.2f slope %.4f rms %.2f' % (-(lT[0] * 590 + lT[2]) / lT[1], -lT[0] / lT[1], rt.std())
        np.save('board23_lines.npy', np.array([lL, lR, lT, lB]))
    print(s)
