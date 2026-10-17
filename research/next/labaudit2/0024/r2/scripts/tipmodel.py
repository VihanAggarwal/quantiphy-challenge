"""Book tipping over the slope foot: leading bottom edge on the table at x beyond the foot, trailing bottom edge on the
incline at s up the slope, |L-T| = w (book width along the motion, 9.0 cm). Solve (x, across a) per frame so that the
book's top-surface centre projects onto the tracked centre. x<0 means still fully on the incline (s = along of the
leading edge)."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from geom import *
from motion import uv, cap, HB
W = 0.090; Hb = 0.0146
c32 = up_dir @ (-n)  # not used; build a horizontal outward direction
d_out = np.cross(n, e); d_out /= np.linalg.norm(d_out)
if d_out @ up_dir > 0: d_out = -d_out    # away from the board
def top_centre(x, a):
    foot = BR + e * a
    if x <= 0:   # flat on the incline, leading edge at along -x
        L = foot + up_dir * (-x); T = L + up_dir * W
    elif x < W:
        # solve s: |x d_out - s up_dir| = W
        b = -2 * x * (d_out @ up_dir); cc = x * x - W * W
        s = (-b + np.sqrt(max(b * b - 4 * cc, 0))) / 2
        L = foot + d_out * x; T = foot + up_dir * s
    else:
        L = foot + d_out * x; T = foot + d_out * (x - W)
    M = (L + T) / 2; u = (T - L) / np.linalg.norm(T - L)
    nrm = np.cross(e, u); nrm /= np.linalg.norm(nrm)
    if nrm @ n < 0: nrm = -nrm
    return M + nrm * Hb
def proj(X): return np.array([711 * X[0] / X[2] + 640, 711 * X[1] / X[2] + 360])
def solve(u, v, x0=0.0, a0=0.1):
    p = np.array([x0, a0])
    for _ in range(60):
        f = proj(top_centre(*p)) - [u, v]
        J = np.zeros((2, 2))
        for k in range(2):
            dp = np.zeros(2); dp[k] = 1e-5; J[:, k] = (proj(top_centre(*(p + dp))) - proj(top_centre(*p))) / 1e-5
        st = np.linalg.lstsq(J, f, rcond=None)[0]
        st = np.clip(st, -0.01, 0.01); p = p - st
    return p, np.linalg.norm(proj(top_centre(*p)) - [u, v])
if __name__ == '__main__':
    for tag in 'osx':
        P = {}; line = ''
        for k in range(24, 37):
            p, err = solve(*uv(tag, k))
            P[k] = top_centre(*p)
            line += ' v%d x=%.1f a=%.1f r=%.3f|' % (k, p[0] * 100, p[1] * 100, np.linalg.norm(P[k]))
        print(tag, line)
        sp = ' '.join('c%d->%d:%.0f' % (cap(k), cap(k + 1), np.linalg.norm(P[k + 1] - P[k]) * 2500 / (cap(k + 1) - cap(k))) for k in range(24, 36))
        print('   speeds', sp)
        lab = np.linalg.norm(ray(*uv(tag, 30)) * (0.977 + np.linalg.norm(P[30]) - np.linalg.norm(P[29])) - ray(*uv(tag, 29)) * 0.977) * 2500
        lab1 = np.linalg.norm(ray(*uv(tag, 25)) * (1.0685 + np.linalg.norm(P[25]) - np.linalg.norm(P[24])) - ray(*uv(tag, 24)) * 1.0685) * 2500
        print('   label-style (stated anchor + tip-model range change): v(1.0) %.0f  v(1.2) %.0f' % (lab1, lab))
