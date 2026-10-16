import cv2, numpy as np
def sub_drop(col, lo, hi):
    """subpixel location of steepest luminance change (either sign) in col[lo:hi]."""
    d = col[lo + 1:hi] - col[lo:hi - 1]
    i = np.argmax(np.abs(d))
    # parabolic refine on |d|
    a = np.abs(d)
    if 0 < i < len(a) - 1:
        den = a[i - 1] - 2 * a[i] + a[i + 1]
        off = 0.5 * (a[i - 1] - a[i + 1]) / den if den != 0 else 0
    else:
        off = 0
    return lo + i + 0.5 + off
def edges(img, xs):
    g = img.astype(float).mean(2)
    g = cv2.GaussianBlur(g, (1, 3), 0)
    far, near = [], []
    for x in xs:
        col = g[:, x - 1:x + 2].mean(1)
        far.append((x, sub_drop(col, 474, 489)))
        near.append((x, sub_drop(col, 491, 502)))
    return np.array(far), np.array(near)
xs = list(range(505, 641, 3))
out = {}
for tag in ['0023', '0023s', '0023x']:
    for fr in range(40, 49):
        img = cv2.imread('f_%s_%02d.png' % (tag, fr))
        F, N = edges(img, xs)
        pf = np.polyfit(F[:, 0], F[:, 1], 1); pn = np.polyfit(N[:, 0], N[:, 1], 1)
        rf = F[:, 1] - np.polyval(pf, F[:, 0]); rn = N[:, 1] - np.polyval(pn, N[:, 0])
        out[(tag, fr)] = (pf, pn)
        print(tag, fr, 'far: y=%.4fx+%.2f (rms %.2f) @565 %.2f | near: y=%.4fx+%.2f (rms %.2f) @565 %.2f | dy %.2f' % (
            pf[0], pf[1], rf.std(), np.polyval(pf, 565), pn[0], pn[1], rn.std(), np.polyval(pn, 565), np.polyval(pn, 565) - np.polyval(pf, 565)))
np.save('rest23_lines.npy', np.array([[*out[k][0], *out[k][1]] for k in out]))
