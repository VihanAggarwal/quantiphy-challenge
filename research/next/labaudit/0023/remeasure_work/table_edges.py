import cv2, numpy as np
f = cv2.imread('f_0023x_48.png').astype(float)
g = f.sum(2)/3
# side edges: for each row, find x where table (bright) meets black background
def edge_x(y, side):
    row = g[y]
    if side=='L':
        xs = range(250, 600)
        for x in xs:
            if row[x] > 60:  # first non-black
                # subpixel: interpolate threshold 0.5*(table level)
                lev = np.median(row[x+3:x+10]); th = lev/2
                x0 = x-3
                for xx in range(x0, x+6):
                    if row[xx] < th <= row[xx+1]:
                        return xx + (th-row[xx])/(row[xx+1]-row[xx])
                return x
    else:
        for x in range(1000, 680, -1):
            if row[x] > 60:
                lev = np.median(row[x-10:x-3]); th = lev/2
                for xx in range(x+3, x-6, -1):
                    if row[xx] < th <= row[xx-1]:
                        return xx - (th-row[xx])/(row[xx-1]-row[xx])
                return x
res = {}
for side in 'LR':
    pts = []
    for y in range(450, 526):
        x = edge_x(y, side)
        if x is not None: pts.append((x, y))
    pts = np.array(pts)
    A = np.c_[pts[:,1], np.ones(len(pts))]
    coef, *_ = np.linalg.lstsq(A, pts[:,0], rcond=None)
    resid = pts[:,0] - A@coef
    print(side, 'x = %.4f*y + %.2f' % tuple(coef), 'rms %.2f' % resid.std(), 'max %.2f' % abs(resid).max())
    # check curvature: fit quadratic
    c2 = np.polyfit(pts[:,1], pts[:,0], 2); print('   quad coef', c2)
    res[side] = coef
# intersection
aL,bL = res['L']; aR,bR = res['R']
y = (bR-bL)/(aL-aR); x = aL*y+bL
print('VP side edges: x=%.1f y=%.1f' % (x, y))
# front edge row of table top: find in columns the transition table top -> front face (darker)
for xc in [300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900]:
    col = g[500:560, xc]
    d = np.diff(col)
    i = np.argmin(d)  # strongest drop (top surface bright -> edge darker)
    print('front edge col', xc, 'row ~', 500+i, ' vals', col[i-3:i+4].astype(int))
