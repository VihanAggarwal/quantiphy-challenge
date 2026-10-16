"""Vertical vanishing point of camera b from wall seams / door edges picked from LSD on b_00 (see b_lines.png)."""
import numpy as np
F, CX, CY = 711.0, 640.0, 360.0
segs = {11: (135, 328, 41, 0), 8: (244, 0, 290, 283), 20: (396, 79, 407, 249), 18: (410, 249, 396, 46), 21: (503, 151, 503, 222),
        24: (505, 222, 506, 98), 5: (722, 132, 746, 0), 10: (851, 84, 874, 0), 14: (917, 88, 939, 0), 13: (852, 147, 829, 238),
        17: (814, 132, 797, 214), 16: (1154, 358, 1192, 250), 15: (1241, 483, 1260, 416)}
def hl(x1, y1, x2, y2):
    p = np.array([(x1 - CX) / F, (y1 - CY) / F, 1.0]); q = np.array([(x2 - CX) / F, (y2 - CY) / F, 1.0])
    l = np.cross(p, q); return l / np.linalg.norm(l)
def vp(keys):
    H = np.array([hl(*segs[k]) for k in keys]); W = np.array([np.hypot(segs[k][2] - segs[k][0], segs[k][3] - segs[k][1]) for k in keys])
    M = (H * W[:, None]).T @ H; ev, evec = np.linalg.eigh(M); v = evec[:, 0]
    if v[1] < 0: v = -v
    return v, np.abs(H @ v)
for name, keys in (('walls', [11, 8, 20, 18, 21, 24]), ('walls+door', [11, 8, 20, 18, 21, 24, 5]), ('all', list(segs))):
    v, r = vp(keys)
    vpx = (v[0] / v[2] * F + CX, v[1] / v[2] * F + CY) if abs(v[2]) > 1e-6 else None
    print(name, 'g_cam', np.round(v, 4), 'pitch_down %.1f deg' % np.degrees(np.arcsin(v[2])), 'roll %.1f' % np.degrees(np.arctan2(v[0], v[1])),
          'VP px', np.round(vpx, 0), 'resid', np.round(r * 1000, 1))
