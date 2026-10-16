import numpy as np
# slope plane from the two stated depth labels + horizontal direction of the board top/bottom edges
f, cx, cy = 711., 640., 360.
K = np.array([[f, 0, cx], [0, f, cy], [0, 0, 1]]); Ki = np.linalg.inv(K)
ray = lambda p: Ki @ np.r_[p, 1.0]
def at_range(p, r):
    v = ray(p); return v / np.linalg.norm(v) * r
dh = ray((12353.55, 356.5)); dh /= np.linalg.norm(dh)
def solve(top_row=356.5, bot_row=482.37, rtop=1.201, rbot=0.9555, t=0.0146, label=''):
    A = at_range((590, top_row), rtop); B = at_range((590, bot_row), rbot)
    dd = A - B; Ls = np.linalg.norm(dd); dd /= Ls
    ns = np.cross(dd, dh); ns /= np.linalg.norm(ns); ns = -ns if ns[2] > 0 else ns
    ds = ns @ B + t
    P = lambda p: ray(p) * ds / (ns @ ray(p))
    FLc, FRc, NLc, NRc = P((533.5, 350.3)), P((649.5, 350.3)), P((530.3, 379.0)), P((653.6, 379.0))
    Lf = np.linalg.norm(FRc - FLc); Ln = np.linalg.norm(NRc - NLc)
    Wl = np.linalg.norm(FLc - NLc); Wr = np.linalg.norm(FRc - NRc)
    # angle of slope relative to camera horizontal (y-down camera)
    ang = np.degrees(np.arctan2(-dd[1], np.hypot(dd[0], dd[2])))
    print('%-38s slope L %.2f ang(cam) %.1f | book L %.2f/%.2f W %.2f/%.2f  W/L %.3f' % (label, 100 * Ls, ang, 100 * Lf, 100 * Ln, 100 * Wl, 100 * Wr, (Wl + Wr) / (Lf + Ln)))
solve(label='labels at edges (356.5 / 482.4)')
solve(top_row=362, label='far click 5px inside top edge')
solve(top_row=362, bot_row=477, label='both clicks 5px inside')
solve(top_row=380, bot_row=460, label='clicks well inside (380/460)')
