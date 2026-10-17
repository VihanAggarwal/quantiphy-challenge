import numpy as np
r = np.load('t59b.npy'); d = np.load('d59.npy')
fps = 30.
ii = r[:, 0]; x = r[:, 1] - r[:, 5]; y = r[:, 2] - r[:, 6]
good = (d[:, 1] > 100) & (d[:, 1] < 145) & ~np.isin(d[:, 0], [77, 80, 91, 93])
dd = d[good]
pd = np.polyfit(dd[:, 0] / fps, dd[:, 1], 2)
print('diam fit (quad) coeffs', pd, ' d(66)=%.1f d(75)=%.1f d(81)=%.1f d(90)=%.1f d(97)=%.1f' % tuple(np.polyval(pd, np.array([66, 75, 81, 90, 97]) / fps)))
pl = np.polyfit(dd[:, 0] / fps, dd[:, 1], 1)
print('diam lin', pl)
sel = (ii >= 66) & (ii <= 97)
t = ii[sel] / fps
for name, dfun in [('quad', lambda tt: np.polyval(pd, tt)), ('lin', lambda tt: np.polyval(pl, tt)), ('const129', lambda tt: 129.0 + 0 * tt)]:
    dt = dfun(t)
    for cyy in (540, 400, 680):
        YD = (y[sel] - cyy) / dt; XD = (x[sel] - 960) / dt
        p = np.polyfit(t, YD, 2)
        aD = 2 * p[0]
        D = 9.8 / aD
        res = YD - np.polyval(p, t)
        print(name, 'cy', cyy, 'a=%.3f diam/s2 -> D=%.4f m  rms=%.3f' % (aD, D, res.std()))
# sub-ranges with quad d
for a, b in [(66, 81), (81, 97), (66, 90), (70, 97)]:
    s2 = (ii >= a) & (ii <= b); tt = ii[s2] / fps
    YD = (y[s2] - 540) / np.polyval(pd, tt)
    p = np.polyfit(tt, YD, 2); print('range', a, b, 'D=%.4f' % (9.8 / (2 * p[0])))
