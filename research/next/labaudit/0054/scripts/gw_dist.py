"""Green-white centre distance at 1.0 s: a (stated ranges at the n24 centres), a fits, b fits, b stated ranges at n24 centres."""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ballistic_a as BA, ballistic_b as BB
from ballistic_a import F, CX, CY
def ray(u, v):
    d = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return d / np.linalg.norm(d)
print('a stated, n24 centres G(600.0,291.8) W(570.3,272.1): %.3f' % np.linalg.norm(3.039 * ray(600.0, 291.8) - 3.0735 * ray(570.3, 272.1)))
for p in (1.0, 2.5):
    g = BA.fit(BA.green, list(range(24, 36)), p); w = BA.fit(BA.white, list(range(29, 36)), p)
    print('a fits pitch %.1f: dist(1.0) %.3f  dist(1.04) %.3f' % (p, np.linalg.norm(g['pos'](1.0) - w['pos'](1.0)), np.linalg.norm(g['pos'](1.04) - w['pos'](1.04))))
for kw in (dict(pitch=29.9, roll=-6.5), dict()):
    o = BB.fit_joint([BB.green, BB.white], [list(range(25, 36)), [21, 22, 23] + list(range(25, 36))], **kw)
    G, W = o['balls']
    print('b fits %s: dist(1.0) %.3f dist(1.04) %.3f' % (kw or 'free', np.linalg.norm(G['pos'](1.0) - W['pos'](1.0)), np.linalg.norm(G['pos'](1.04) - W['pos'](1.04))))
# b stated ranges at n24: centres from the fits' projections at 1.0 (blob is merged)
o = BB.fit_joint([BB.green, BB.white], [list(range(25, 36)), [21, 22, 23] + list(range(25, 36))], pitch=29.9, roll=-6.5)
G, W = o['balls']; pg, pw = G['pos'](1.0), W['pos'](1.0)
ug = (F * pg[0] / pg[2] + CX, F * pg[1] / pg[2] + CY); uw = (F * pw[0] / pw[2] + CX, F * pw[1] / pw[2] + CY)
print('b projected centres at 1.0: G (%.1f,%.1f) W (%.1f,%.1f); stated-range distance %.3f' % (ug + uw + (np.linalg.norm(1.331 * ray(*ug) - 1.235 * ray(*uw)),)))
