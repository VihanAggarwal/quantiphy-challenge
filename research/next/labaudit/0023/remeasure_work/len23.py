import numpy as np
lL, lR, lF = np.load('plane23_lines.npy')
def inter(a, b):
    p = np.cross(a, b); return p[:2] / p[2]
VPs = inter(lL, lR); FL = inter(lL, lF); FR = inter(lR, lF)
L = np.load('rest23_lines.npy'); af, bf, an, bn = np.median(L, 0)
f, cx, cy, t = 711., 640., 360., 0.0146
K = np.array([[f, 0, cx], [0, f, cy], [0, 0, 1]]); Ki = np.linalg.inv(K)
ray = lambda p: Ki @ np.r_[p, 1.0]
d_side = ray(VPs); d_side /= np.linalg.norm(d_side)
nF = K.T @ lF; nF /= np.linalg.norm(nF)
d_front = np.cross(nF, d_side); d_front /= np.linalg.norm(d_front)
n = np.cross(d_side, d_front); n /= np.linalg.norm(n); n = n if n[1] > 0 else -n
P = lambda p, h: ray(p) * h / (n @ ray(p))
for name, h in [('S1 front=60.3', 0.1693), ('S2 depth', 0.1775)]:
    ht = h - t
    fl = (479.0, af * 479.0 + bf); nl = (479.3, an * 479.3 + bn)
    for hyp, xr_far, xr_near in [('right end incl. whitish', 646.0, 657.5), ('right end blue only', 640.5, 652.0)]:
        fr = (xr_far, af * xr_far + bf); nr = (xr_near, an * xr_near + bn)
        Pfl, Pnl, Pfr, Pnr = [P(p, ht) for p in (fl, nl, fr, nr)]
        Lfar = np.linalg.norm(Pfr - Pfl); Lnear = np.linalg.norm(Pnr - Pnl)
        Wl = np.linalg.norm(Pfl - Pnl); Wr = np.linalg.norm(Pfr - Pnr)
        u = (Pnr - Pnl) / Lnear; v = (Pfl - Pnl) / Wl
        print('%-14s %-24s L far %.2f near %.2f | W left %.2f right %.2f | corner angle %.1f' % (name, hyp, 100 * Lfar, 100 * Lnear, 100 * Wl, 100 * Wr, np.degrees(np.arccos(u @ v))))
    # where is the book centre and what range would the clicked centre have?
    c = P((565, 0.5 * (af * 565 + bf + an * 565 + bn)), ht)
    print('   top-face centre 3D', np.round(c, 4), 'range %.4f' % np.linalg.norm(c))
