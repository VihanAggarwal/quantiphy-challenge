import cv2, numpy as np
img = cv2.imread('f_0023x_48.png').astype(float)
g = img.mean(2)
def fit_line(pts):
    pts = np.asarray(pts, np.float32)
    vx, vy, x0, y0 = cv2.fitLine(pts, cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
    n = np.array([-vy, vx]); c = -n @ np.array([x0, y0]); return np.array([n[0], n[1], c])
def inter(a, b):
    p = np.cross(a, b); return p[:2] / p[2]
# table front edge (top surface -> front face drop)
F = []
for x in list(range(300, 470, 2)) + list(range(680, 905, 2)):
    col = g[515:545, x - 1:x + 2].mean(1)
    d = col[1:] - col[:-1]; i = np.argmin(d)
    a = -d
    off = 0.5 * (a[i - 1] - a[i + 1]) / (a[i - 1] - 2 * a[i] + a[i + 1]) if 0 < i < len(a) - 1 else 0
    F.append((x, 515 + i + 0.5 + off))
F = np.array(F); lF = fit_line(F)
r = F @ lF[:2] + lF[2]; print('front edge rms', r.std(), 'slope', -lF[0] / lF[1])
q = np.polyfit(F[:, 0], F[:, 1], 2); print('front quad', q)
# side edges (reuse method)
def side(sidech):
    pts = []
    for y in range(450, 526):
        row = g[y]
        if sidech == 'L':
            xs = np.where(row[250:600] > 60)[0]; x = 250 + xs[0]
            lev = np.median(row[x + 3:x + 10]); th = lev / 2
            for xx in range(x - 3, x + 6):
                if row[xx] < th <= row[xx + 1]:
                    pts.append((xx + (th - row[xx]) / (row[xx + 1] - row[xx]), y)); break
        else:
            xs = np.where(row[680:1000] > 60)[0]; x = 680 + xs[-1]
            lev = np.median(row[x - 10:x - 3]); th = lev / 2
            for xx in range(x + 3, x - 6, -1):
                if row[xx] < th <= row[xx - 1]:
                    pts.append((xx - (th - row[xx]) / (row[xx - 1] - row[xx]), y)); break
    return fit_line(pts)
lL = side('L'); lR = side('R')
VPs = inter(lL, lR); FL = inter(lL, lF); FR = inter(lR, lF)
print('VP side', VPs, 'FL', FL, 'FR', FR)
np.save('plane23_lines.npy', np.array([lL, lR, lF]))
