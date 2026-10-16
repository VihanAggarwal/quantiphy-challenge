import cv2, numpy as np
def fit_line(pts):
    pts = np.asarray(pts, np.float32)
    vx, vy, x0, y0 = cv2.fitLine(pts, cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
    n = np.array([-vy, vx]); c = -n @ np.array([x0, y0]); return np.array([n[0], n[1], c])
def inter(a, b):
    p = np.cross(a, b); return p[:2] / p[2]
# board lines from frame 0 (left/right/bottom) and frame 48 (top)
def xline(a, b):  # x = a*y + b  ->  homogeneous
    return np.array([1.0, -a, -b])
def yline(a, b, x0=0):  # y = a*(x - x0) + b
    return np.array([-a, 1.0, -(b - a * x0)])
lL = xline(-0.2050, 590.8); lR = xline(0.1484, 606.2)
lB = yline(-0.0107, 482.37, 590); lT = yline(0.0, 356.5, 590)
TL, TR, BR, BL = inter(lL, lT), inter(lR, lT), inter(lR, lB), inter(lL, lB)
print('board corners TL', TL, 'TR', TR, 'BR', BR, 'BL', BL)
VPd = inter(lL, lR); VPh = inter(lT, lB)
print('VP dip', VPd, 'VP horiz', VPh)
# table model
tl = np.load('plane23_lines.npy'); VPs = inter(tl[0], tl[1]); lF = tl[2]
def model(f=711., cx=640., cy=360., h_table=0.1775, t=0.0146, ytop=350.3, ybot=379.0, xs=(575, 605), use_tableh=True, verbose=False):
    K = np.array([[f, 0, cx], [0, f, cy], [0, 0, 1]]); Ki = np.linalg.inv(K)
    ray = lambda p: Ki @ np.r_[p, 1.0]
    # table plane
    d_side = ray(VPs); d_side /= np.linalg.norm(d_side)
    nF = K.T @ lF; nF /= np.linalg.norm(nF)
    d_front = np.cross(nF, d_side); d_front /= np.linalg.norm(d_front)
    nt = np.cross(d_side, d_front); nt /= np.linalg.norm(nt); nt = nt if nt[1] > 0 else -nt
    # slope plane: dip direction from VPd, horizontal from board top/bottom lines (VPh) 
    dd = ray(VPd); dd /= np.linalg.norm(dd)
    dh = ray(VPh); dh /= np.linalg.norm(dh)
    ns = np.cross(dd, dh); ns /= np.linalg.norm(ns)
    if ns[2] > 0: ns = -ns        # normal pointing toward camera (negative z)
    # slope plane passes through bottom edge on table: point at bottom-centre
    pb = (590, 482.37)
    Xb = ray(pb) * h_table / (nt @ ray(pb))
    if not use_tableh:
        Xb = ray(pb) / np.linalg.norm(ray(pb)) * 0.9555 * 1.0
    ds = ns @ Xb                   # plane: ns.X = ds  (ds<0 since ns toward camera)
    P = lambda p, d: ray(p) * d / (ns @ ray(p))
    # board geometry
    C = {k: P(v, ds) for k, v in dict(TL=TL, TR=TR, BR=BR, BL=BL).items()}
    Ls = 0.5 * (np.linalg.norm(C['TL'] - C['BL']) + np.linalg.norm(C['TR'] - C['BR']))
    Ws_top = np.linalg.norm(C['TL'] - C['TR']); Ws_bot = np.linalg.norm(C['BL'] - C['BR'])
    ang_table = np.degrees(np.arccos(abs(ns @ nt)))
    rng_top = np.linalg.norm(P((590, 356.5), ds)); rng_bot = np.linalg.norm(P(pb, ds))
    # book top face plane: offset t toward camera (|ds| decreases)
    db = ds + t                   # ns points toward camera: ns.X = ds (negative); moving toward camera increases ns.X
    Ws = []
    for x in xs:
        A = P((x, ytop), db); B = P((x, ybot), db)
        v = A - B; Ws.append(np.linalg.norm(v - (v @ dh) * dh))
    if verbose:
        print('  slope angle vs table %.1f deg; board L %.2f, W top %.2f bot %.2f; range top %.3f (label 1.201) bot %.3f (label 0.9555)' % (ang_table, 100 * Ls, 100 * Ws_top, 100 * Ws_bot, rng_top, rng_bot))
    return 100 * np.mean(Ws), dict(Ls=Ls, ang=ang_table, rt=rng_top, rb=rng_bot)
for ht in [0.1693, 0.1775]:
    print('table h', ht)
    W, _ = model(h_table=ht, verbose=True); print('  book W (frame 10, top face 350.3-379.0) = %.2f cm' % W)
print('anchor by slope-near depth label instead of table:')
W, _ = model(use_tableh=False, verbose=True); print('  book W = %.2f' % W)
print('sensitivity:')
for kw in [dict(ytop=349.8), dict(ytop=350.8), dict(ybot=378.5), dict(ybot=379.5), dict(t=0.0), dict(t=0.02), dict(f=690), dict(f=730), dict(cy=345), dict(cy=375), dict(cx=600)]:
    W, d = model(**kw); print('  ', kw, 'W=%.2f  (slope ang %.1f, board L %.1f)' % (W, d['ang'], 100 * d['Ls']))
print('--- book L on slope (frame 10) and W/L ratio')
def LW(f=711., cx=640., cy=360., h_table=0.1775, t=0.0146, use_tableh=True):
    K = np.array([[f, 0, cx], [0, f, cy], [0, 0, 1]]); Ki = np.linalg.inv(K)
    ray = lambda p: Ki @ np.r_[p, 1.0]
    d_side = ray(VPs); d_side /= np.linalg.norm(d_side)
    nF = K.T @ lF; nF /= np.linalg.norm(nF)
    d_front = np.cross(nF, d_side); d_front /= np.linalg.norm(d_front)
    nt = np.cross(d_side, d_front); nt /= np.linalg.norm(nt); nt = nt if nt[1] > 0 else -nt
    dd = ray(VPd); dd /= np.linalg.norm(dd); dh = ray(VPh); dh /= np.linalg.norm(dh)
    ns = np.cross(dd, dh); ns /= np.linalg.norm(ns); ns = -ns if ns[2] > 0 else ns
    pb = (590, 482.37)
    Xb = ray(pb) * h_table / (nt @ ray(pb)) if use_tableh else ray(pb) / np.linalg.norm(ray(pb)) * 0.9555
    db = ns @ Xb + t
    P = lambda p: ray(p) * db / (ns @ ray(p))
    # corners of top face: far edge row 350.3 (x 533.5..649.5), near edge row 379.0 (x 530.3..653.6)
    FLc, FRc, NLc, NRc = P((533.5, 350.3)), P((649.5, 350.3)), P((530.3, 379.0)), P((653.6, 379.0))
    Lf = np.linalg.norm(FRc - FLc); Ln = np.linalg.norm(NRc - NLc)
    Wl = np.linalg.norm(FLc - NLc); Wr = np.linalg.norm(FRc - NRc)
    return 100 * Lf, 100 * Ln, 100 * Wl, 100 * Wr
for ht in [0.1693, 0.1775]:
    Lf, Ln, Wl, Wr = LW(h_table=ht)
    print('h %.4f: L far %.2f near %.2f | W left %.2f right %.2f | W/L %.3f' % (ht, Lf, Ln, Wl, Wr, (Wl + Wr) / (Lf + Ln)))
