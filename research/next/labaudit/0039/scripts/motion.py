"""Displacement 1.0->1.5 s and velocity at 1.0 s of the white (ping-pong) ball.
Centre pixel: horizontal = mid of the white blob's left/right extent, vertical = top + half width (lower half is shaded).
Route A: stated ranges (1.014 at f24, 0.737 at f36); range for other frames from apparent size (D=4 cm) rescaled to the anchors.
Route B: ball centre on the plane 2 cm above the table top (rolling ball), h from table.py (+-2%)."""
import numpy as np, json
B = '/home/user/quantiphy-challenge/research/next/labaudit/0039'
F, CX, CY = 711.0, 640.0, 360.0
pl = np.load(f'{B}/plane.npy'); n, d0 = pl[:3], pl[3]
bf = json.load(open(f'{B}/ballfit.json'))
def ray(u, v):
    r = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return r / np.linalg.norm(r)
for rend in ['0039', '0039s']:
    T = {int(k): v for k, v in bf[rend].items()}
    px = {i: np.array([(t['l'] + t['rr']) / 2, t['top'] + (t['rr'] - t['l'] + 1) / 2]) for i, t in T.items()}
    wid = {i: t['rr'] - t['l'] + 1 for i, t in T.items()}
    print('==', rend, 'f24 px', px[24], 'f36 px', px[36], 'width', wid[24], wid[36])
    # size-based range (tangential width ~ f D / range); rescale to anchors
    rs = {i: F * 0.04 / wid[i] for i in px}
    print('  size range f24 %.3f f36 %.3f (stated 1.014, 0.737)' % (rs[24], rs[36]))
    P24 = 1.014 * ray(*px[24]); P36 = 0.737 * ray(*px[36])
    print('  Route A displacement %.2f cm' % (np.linalg.norm(P36 - P24) * 100))
    # lateral-only / depth-only components
    print('    range change %.2f, lateral %.2f' % (27.7, np.linalg.norm(P36 - P24 - ((P36 - P24) @ ray(*px[24])) * ray(*px[24])) * 100))
    for h in (d0 * 0.98, d0, d0 * 1.02):
        def onb(p): r = ray(*p); return (h - 0.02) / (n @ r) * r
        Q = {i: onb(px[i]) for i in px}
        print('  Route B h=%.4f: f24 range %.3f f36 range %.3f, displacement %.2f' % (h, np.linalg.norm(Q[24]), np.linalg.norm(Q[36]), np.linalg.norm(Q[36] - Q[24]) * 100))
        v = {k: np.linalg.norm(Q[k + 1] - Q[k]) * 24 * 100 for k in range(20, 40) if k in Q and k + 1 in Q}
        print('    step speeds cm/s:', ' '.join('%d:%.0f' % (k, v[k]) for k in sorted(v)))
        print('    v(1.0) fwd 24->25 %.1f, central 23->25 %.1f, 24->26 /2 %.1f, mean 20-28 %.1f' % (
            v[24], np.linalg.norm(Q[25] - Q[23]) * 12 * 100, np.linalg.norm(Q[26] - Q[24]) * 12 * 100, np.linalg.norm(Q[28] - Q[20]) * 3 * 100))
    # Route A velocity: interpolate range linearly between anchors in time (and size-based alternative)
    for lab, rng in [('lin-time', lambda i: 1.014 + (0.737 - 1.014) * (i - 24) / 12),
                     ('size*k', lambda i: rs[i] * (1.014 / rs[24] if i <= 30 else 0.737 / rs[36]))]:
        Q = {i: rng(i) * ray(*px[i]) for i in range(20, 41)}
        print('  Route A %s: v fwd 24->25 %.1f, central 23->25 %.1f, 24->26 %.1f, disp %.2f' % (lab,
              np.linalg.norm(Q[25] - Q[24]) * 2400, np.linalg.norm(Q[25] - Q[23]) * 1200, np.linalg.norm(Q[26] - Q[24]) * 1200, np.linalg.norm(Q[36] - Q[24]) * 100))
