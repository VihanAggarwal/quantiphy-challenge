import cv2, numpy as np
L = np.load('rest23_lines.npy'); af, bf, an, bn = np.median(L, 0)
def end_edges(img):
    g = img.astype(float).mean(2)
    left, right = [], []
    for y in range(484, 497):
        row = g[y]
        # left: transition from table (~137) to face (~205) scanning x 465..495
        seg = row[466:496]; face = np.median(row[485:500]); tab = np.median(row[455:466])
        th = 0.5 * (face + tab)
        for i in range(len(seg) - 1, 0, -1):
            if seg[i - 1] < th <= seg[i] and all(seg[i:i + 4] > th - 5):
                left.append((466 + i - 1 + (th - seg[i - 1]) / (seg[i] - seg[i - 1]), y)); break
    for y in range(479, 492):
        row = g[y]
        yfar = af * 640 + bf; ynear = an * 640 + bn
        face = np.median(row[600:630]); tab = np.median(row[668:680]); th = 0.5 * (face + tab)
        seg = row[620:672]
        for i in range(1, len(seg)):
            if seg[i - 1] >= th > seg[i]:
                right.append((620 + i - 1 + (seg[i - 1] - th) / (seg[i - 1] - seg[i]), y)); break
    return np.array(left), np.array(right)
for tag in ['0023', '0023s', '0023x']:
    for fr in [46, 47, 48]:
        l, r = end_edges(cv2.imread('f_%s_%02d.png' % (tag, fr)))
        pl = np.polyfit(l[:, 1], l[:, 0], 1); pr = np.polyfit(r[:, 1], r[:, 0], 1)
        print(tag, fr, 'left x=%.3fy+%.1f (n%d, x@far %.1f x@near %.1f)' % (pl[0], pl[1], len(l), np.polyval(pl, 484.5), np.polyval(pl, 499)),
              ' right x=%.3fy+%.1f (n%d)' % (pr[0], pr[1], len(r)))
        print('    right pts', np.round(r, 1).tolist())
