import numpy as np, cv2
fr = np.load('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/fr0018.npy')
def half_level_cross(profile, lo, hi, start, direction):
    """sub-pixel position where profile crosses (lo+hi)/2 walking from start in direction"""
    lvl = (lo + hi) / 2.0
    i = start
    while 0 < i < len(profile) - 1:
        a, b = profile[i], profile[i + direction]
        if (a - lvl) * (b - lvl) <= 0 and a != b:
            return i + direction * (a - lvl) / (a - b)
        i += direction
    return np.nan
res = []
for f in range(0, 29):
    g = cv2.cvtColor(fr[f], cv2.COLOR_BGR2GRAY).astype(float)
    # locate box: brightest column band near x 470-492 in rows 255-270
    widths = []
    for y in range(255, 272):
        row = g[y, 450:520]
        # interior bright level: median of the brightest 8 px in 470..492
        inner = np.sort(row[18:42])[-10:].mean()
        # right background level: x 495..505
        bgR = np.median(row[46:56])
        # left background: there is a skin/arm or wall at 455..465
        bgL = np.median(row[5:14])
        # walk from the box center (x=480 -> idx 30) outward
        xr = half_level_cross(row, bgR, inner, 50, -1)
        xl = half_level_cross(row, bgL, inner, 12, +1)
        widths.append((xl + 450, xr + 450, xr - xl))
    w = np.array(widths)
    # vertical extent: column profile at x where box is unoccluded (x=484..488)
    tops, bots = [], []
    for x in range(482, 489):
        col = g[220:310, x]
        inner = np.median(col[30:60])
        bgT = np.median(col[0:12])
        bgB = np.median(col[78:88])
        yt = half_level_cross(col, bgT, inner, 10, +1)
        yb = half_level_cross(col, bgB, inner, 80, -1)
        tops.append(yt + 220); bots.append(yb + 220)
    res.append((f, np.median(w[:, 0]), np.median(w[:, 1]), np.median(w[:, 2]), np.median(tops), np.median(bots)))
    print('f%02d xl %.1f xr %.1f width %.2f px | top %.1f bot %.1f height %.2f px' % (f, res[-1][1], res[-1][2], res[-1][3], res[-1][4], res[-1][5], res[-1][5] - res[-1][4]))
r = np.array(res)
print('median width %.2f  (IQR %.2f-%.2f); median height %.2f' % (np.median(r[:, 3]), np.percentile(r[:, 3], 25), np.percentile(r[:, 3], 75), np.median(r[:, 5] - r[:, 4])))
