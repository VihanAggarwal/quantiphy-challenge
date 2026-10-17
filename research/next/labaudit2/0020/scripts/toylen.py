# Static check: toy length (body + crown) and jar extents from the x-render green-screen silhouette.
# Length = extent along the principal axis (2-98 pct), deblurred by subtracting the per-frame image step projected on
# that axis times an exposure fraction (0 / 0.3 / 0.5), scaled with the fit range (fixed and free gravity) at that frame.
import sys; sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0020/scripts')
from common import *
from track2 import fg_mask
import ballfit as BF
T2 = json.load(open(D + 'track2.json'))
fr = frames('x')

def silhouette(k, uv, win=45):
    im = fr[k]; fg = fg_mask(im, 'x')
    u0, v0 = int(round(uv[0])), int(round(uv[1]))
    x0, y0 = max(0, u0 - win), max(0, v0 - win)
    sub = fg[y0:v0 + win, x0:u0 + win].astype(np.uint8)
    sub = cv2.morphologyEx(sub, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(sub)
    k2 = lab[v0 - y0, u0 - x0]
    if k2 == 0:
        k2 = 1 + np.argmax(st[1:, 4])
    ys, xs = np.nonzero(lab == k2)
    touches = (xs.min() == 0) or (ys.min() == 0) or (xs.max() == sub.shape[1] - 1) or (ys.max() == sub.shape[0] - 1)
    return xs + x0, ys + y0, touches

def extents(xs, ys):
    P = np.c_[xs, ys].astype(float); m = P.mean(0)
    w, V = np.linalg.eigh(np.cov((P - m).T)); a1 = V[:, 1]; a2 = V[:, 0]
    p1 = (P - m) @ a1; p2 = (P - m) @ a2
    return a1, np.percentile(p1, 99) - np.percentile(p1, 1), np.percentile(p2, 99) - np.percentile(p2, 1)

for obj, ks, rng, off, fk in (('toy', [14, 15, 16, 17, 19, 20, 21, 22, 23], R_TOY, 0.04, [15, 16, 17, 19, 20, 21, 22, 23, 24]),
                              ('jar', [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25], R_JAR, 0.035, list(range(15, 27)))):
    fits = [BF.fit('x', obj, fk, rng=rng, off=off, gfree=g) for g in (False, True)]
    print('=====', obj)
    for k in ks:
        tr = T2['x'][obj]; uv = tr[str(k)]['c']
        xs, ys, touch = silhouette(k, uv)
        a1, L, W = extents(xs, ys)
        step = np.subtract(tr[str(k + 1)]['c'], tr[str(k - 1)]['c']) / 2 if str(k + 1) in tr and str(k - 1) in tr else np.zeros(2)
        bl = abs(step @ a1); bw = abs(step @ np.array([-a1[1], a1[0]]))
        Rs = [np.linalg.norm(fz['pos'](tau(np.array([k])))) for fz in fits]
        line = f'v{k} touch={int(touch)} axis({a1[0]:+.2f},{a1[1]:+.2f}) L {L:.1f}px W {W:.1f}px step {np.hypot(*step):.1f} (along {bl:.1f}, perp {bw:.1f}) R {Rs[0]:.2f}/{Rs[1]:.2f} |'
        for ef in (0.0, 0.3, 0.5):
            line += f' ef{ef}: L {(L - ef * bl) * np.mean(Rs) / F * 100:.1f} W {(W - ef * bw) * np.mean(Rs) / F * 100:.1f} cm;'
        print(line)
