"""Top-down simulation_0012_segmented: bird mask (non-white below the house) per frame; x-extent (flight direction) and
y-extent (span). Prints per-frame extents and the max-span / plateau-length ratio."""
import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0012_segmented.mp4')
rows = []; i = 0
while True:
    ok, f = c.read()
    if not ok: break
    g = f.astype(int)
    nonwhite = (g.min(axis=2) < 200).astype(np.uint8)
    nonwhite[:760] = 0          # house and its debris are above row ~720
    n, lab, st, cen = cv2.connectedComponentsWithStats(cv2.morphologyEx(nonwhite, cv2.MORPH_CLOSE, np.ones((3,3),np.uint8)))
    if n > 1:
        k = 1 + np.argmax(st[1:, 4])
        rows.append((i, st[k, 0], st[k, 1], st[k, 2], st[k, 3], st[k, 4]))
    i += 1
rows = np.array(rows)
for r in rows: print('f%d x=%d y=%d w=%d h=%d area=%d' % tuple(r))
w, h = rows[:, 3], rows[:, 4]
print('x-extent (length dir): median %.1f, p10 %.1f, min %.1f' % (np.median(w), np.percentile(w, 10), w.min()))
print('y-extent (span dir): max %.1f, p90 %.1f' % (h.max(), np.percentile(h, 90)))
print('ratio max span / median length = %.3f ; / p10 length = %.3f' % (h.max() / np.median(w), h.max() / np.percentile(w, 10)))
