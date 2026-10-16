"""Compare the a and b ballistic solutions: horizontal speed (constant in flight), vertical speed and total speed at
1.0/1.5/1.52 s, apex time, and the per-frame (25 fps capture) forward-difference speeds the label process would see."""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ballistic_a as BA, ballistic_b as BB
def report(tag, vel, gd):
    for t in (1.0, 1.04, 1.48, 1.5, 1.52):
        v = vel(t); vz = v @ gd; vh = np.linalg.norm(v - vz * gd)
        print('  %s t=%.2f |v| %.2f  v_down %.2f  v_horiz %.2f' % (tag, t, np.linalg.norm(v), vz, vh))
    # apex: v_down = 0
    v0 = vel(1.0) @ gd; print('  %s apex at t=%.3f s' % (tag, 1.0 - v0 / 9.8))
for pitch in (1.0, 2.5):
    g = BA.fit(BA.green, list(range(24, 36)), pitch); w = BA.fit(BA.white, list(range(29, 36)), pitch)
    print('camera a pitch', pitch); report('aG', g['vel'], g['gd']); report('aW', w['vel'], w['gd'])
for kw in (dict(pitch=29.9, roll=-6.5), dict()):
    o = BB.fit_joint([BB.green, BB.white], [list(range(25, 36)), [21, 22, 23] + list(range(25, 36))], **kw)
    print('camera b', kw or 'free g'); report('bG', o['balls'][0]['vel'], o['gd']); report('bW', o['balls'][1]['vel'], o['gd'])
