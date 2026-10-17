import cv2, numpy as np
bg = cv2.imread('frames/bg140.png', 0).astype(float)
bgc = cv2.imread('frames/s140/f050.png').astype(float)
# window openings: dark interior vs lit wall. Use column/row profiles inside a band.
def edges(prof, thr):
    idx = np.nonzero(prof < thr)[0]
    return idx
wins = [(846, 970, 616, 779), (668, 784, 376, 535), (1030, 1150, 376, 535), (848, 968, 376, 535), (1030,1150,618,778)]
for (x0, x1, y0, y1) in wins:
    X0, X1, Y0, Y1 = x0-25, x1+25, y0-25, y1+25
    sub = bg[Y0:Y1, X0:X1]
    wall = np.median(np.r_[sub[:, :10].ravel(), sub[:, -10:].ravel()])
    inner = np.median(bg[(y0+y1)//2-20:(y0+y1)//2+20, (x0+x1)//2-40:(x0+x1)//2-10])
    thr = (wall + inner)/2
    rowp = sub[int(0.3*(Y1-Y0)):int(0.7*(Y1-Y0)), :].mean(0)
    colp = np.r_[sub[:, 15:40].mean(1)] if False else sub[:, int(0.15*(X1-X0)):int(0.4*(X1-X0))].mean(1)
    def span(p, thr):
        b = p < thr; ii = np.nonzero(b)[0]
        # subpixel crossing
        a, z = ii[0], ii[-1]
        l = a-1 + (p[a-1]-thr)/(p[a-1]-p[a]); r = z + (p[z]-thr)/(p[z]-p[z+1])
        return l, r
    l, r = span(rowp, thr); t, b = span(colp, thr)
    print('win', (x0,y0), 'wall', round(wall,1), 'inner', round(inner,1), 'x', round(X0+l,1), round(X0+r,1), 'w', round(r-l,1), 'y', round(Y0+t,1), round(Y0+b,1), 'h', round(b-t,1), 'h/w', round((b-t)/(r-l),3))
# neon sign: red channel bright
R = bgc[:, :, 2]; G = bgc[:, :, 1]
for thr in (200, 150, 100):
    m = (R > thr) & (R - G > 60)
    m[:200] = False; m[420:] = False
    ys, xs = np.nonzero(m)
    print('sign red>', thr, xs.min(), xs.max(), xs.max()-xs.min()+1, ys.min(), ys.max(), ys.max()-ys.min()+1)
# white core of letters
W = bgc.min(2)
for thr in (200, 150):
    m = W > thr; m[:200] = False; m[420:] = False; m[:, :550] = False; m[:, 1400:] = False
    ys, xs = np.nonzero(m)
    print('sign white>', thr, xs.min(), xs.max(), xs.max()-xs.min()+1, ys.min(), ys.max(), ys.max()-ys.min()+1)
