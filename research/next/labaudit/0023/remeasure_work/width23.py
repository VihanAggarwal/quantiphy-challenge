import numpy as np
lL, lR, lF = np.load('plane23_lines.npy')
def inter(a, b):
    p = np.cross(a, b); return p[:2] / p[2]
VPs = inter(lL, lR); FL = inter(lL, lF); FR = inter(lR, lF)
# book top-face lines (pooled over renders/frames): y = a x + b
L = np.load('rest23_lines.npy')  # rows: af, bf, an, bn
af, bf, an, bn = np.median(L, 0)
print('book far y=%.4fx+%.2f near y=%.4fx+%.2f' % (af, bf, an, bn))
def run(f=711., cx=640., cy=360., t=0.0146, far_off=0.0, near_off=0.0, verbose=True):
    K = np.array([[f, 0, cx], [0, f, cy], [0, 0, 1]]); Ki = np.linalg.inv(K)
    ray = lambda p: Ki @ np.r_[p, 1.0]
    d_side = ray(VPs); d_side /= np.linalg.norm(d_side)
    nF = K.T @ lF; nF /= np.linalg.norm(nF)        # back-projected plane of front edge
    d_front = np.cross(nF, d_side); d_front /= np.linalg.norm(d_front)
    n = np.cross(d_side, d_front); n /= np.linalg.norm(n)
    if n[1] < 0: n = -n                               # table below camera: n points down (+y)
    # plane n.X = h ; scale options
    P = lambda p, h: ray(p) * h / (n @ ray(p))
    # S1: front edge = 60.3 cm
    h1 = 0.603 / np.linalg.norm(P(FL, 1) - P(FR, 1))
    res = {}
    for name, h in [('S1_front60.3', h1)]:
        res[name] = h
    # S2: book depth label 0.851 m at book center (top face center at x=565)
    xc = 565; yc = 0.5 * ((af * xc + bf) + (an * xc + bn))
    r = ray((xc, yc)); hb = 0.851 / np.linalg.norm(r) * (n @ r)   # height of top face plane
    res['S2_bookdepth'] = hb + t
    # S3: slope near 0.9555 at board bottom edge (585, 483) on table
    r = ray((585, 483.5)); res['S3_slopenear'] = 0.9555 / np.linalg.norm(r) * (n @ r)
    out = {}
    for name, h in res.items():
        ht = h - t   # top face plane
        x1, x2 = 520, 620
        Fa = P((x1, af * x1 + bf + far_off), ht); Fb = P((x2, af * x2 + bf + far_off), ht)
        Na = P((x1, an * x1 + bn + near_off), ht); Nb = P((x2, an * x2 + bn + near_off), ht)
        u = (Fb - Fa) / np.linalg.norm(Fb - Fa)
        # perpendicular distance from near-edge midpoint to far line, in plane
        M = 0.5 * (Na + Nb); v = M - Fa; w = v - (v @ u) * u
        un = (Nb - Na) / np.linalg.norm(Nb - Na)
        ang = np.degrees(np.arccos(abs(u @ un)))
        rot = np.degrees(np.arccos(abs(u @ d_front)))
        # book length check at rest: horizontal ends of top face (x 479.5 .. 654) at mid rows
        out[name] = (h, np.linalg.norm(w), ang, rot)
        if verbose:
            print('  %-14s table h=%.4f  W=%.2f cm  (far/near edge angle %.1f deg, book rot vs table %.1f deg)' % (name, h, 100 * np.linalg.norm(w), ang, rot))
    return out
print('nominal f=711 pp=(640,360)')
run()
for f in [690, 730]:
    print('f', f); run(f=f)
for cy in [345, 375]:
    print('cy', cy); run(cy=cy)
for cx in [600, 680]:
    print('cx', cx); run(cx=cx)
print('edge offsets: far -0.5 / near +0.5 (outer)'); run(far_off=-0.5, near_off=0.5)
print('edge offsets: far +0.5 / near -0.5 (inner)'); run(far_off=0.5, near_off=-0.5)
print('t=0 vs t=0.02'); run(t=0.0); run(t=0.02)
