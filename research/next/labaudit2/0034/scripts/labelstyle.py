"""Label-style emulation for captured_0034 (camera a = the ToF camera whose depths are stated).
clicks: hue centroid of each ball in ax (track_ax.json); ranges: S = apparent vertical size (vsize_ax.json, smoothed),
scaled to the stated surface range at t=1.2 s (video 29 = capture 30); C = constant range (lateral only);
P = plane fitted to the S-route centres of both balls. Label point = surface point (range r_surface along the click ray).
video k -> capture k (k<=11), k+1 (12..35), k+2 (>=36)."""
import json, sys, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0034/scripts')
from geom import ray, R_BALL
O = '/home/user/quantiphy-challenge/research/next/labaudit2/0034/'
T = json.load(open(O + 'track_ax.json')); VS = json.load(open(O + 'vsize_ax.json'))
STATED = {'L': 0.706, 'R': 0.776}
cap = lambda k: k if k <= 11 else (k + 1 if k <= 35 else k + 2)
N = len(T['L'])

def smooth_size(b, win=7, deg=2):
    h = np.array([d['h'] for d in VS[b]], float); c = np.array([cap(k) for k in range(N)], float)
    out = np.empty(N)
    for k in range(N):
        sel = np.abs(c - c[k]) <= win // 2 + 1
        p = np.polyfit(c[sel], h[sel], deg if sel.sum() > 4 else 1); out[k] = np.polyval(p, c[k])
    return out

def track(b, f, route, click='centroid', plane=None):
    uv = np.array([[d['cx'], d['cy']] for d in T[b]])
    if click == 'mid':      # vertical: midpoint of the measured top/bottom, horizontal: centroid
        uv[:, 1] = [d['mid'] for d in VS[b]]
    rays = np.array([ray(u, v, f) for u, v in uv])
    rc29 = STATED[b] + R_BALL
    if route == 'C':
        rc = np.full(N, rc29)
    elif route == 'S':
        hs = smooth_size(b); rc = rc29 * hs[29] / hs
    elif route == 'P':
        n, d0 = plane                      # n.X = d0 for ball centres
        rc = d0 / (rays @ n)
    C = rays * rc[:, None]                 # centres
    S = rays * (rc - R_BALL)[:, None]      # surface (label) points
    return C, S

def fit_plane(f):
    pts = []
    for b in 'LR':
        C, _ = track(b, f, 'S')
        ks = [k for k in range(N) if not (b == 'L' and k <= 26) and not (b == 'R' and k <= 21) and k != 37]
        pts.append(C[ks])
    P = np.vstack(pts); m = P.mean(0)
    u, s, vt = np.linalg.svd(P - m); n = vt[2]
    if n[1] > 0: n = -n
    res = (P - m) @ n
    return (n, float(n @ m)), float(np.sqrt((res ** 2).mean()))

def speed(S, k):     # forward difference video k -> k+1 on the capture clock
    return np.linalg.norm(S[k + 1] - S[k]) * 25.0 / (cap(k + 1) - cap(k))

def path(S, k0, k1):
    return float(np.linalg.norm(np.diff(S[k0:k1 + 1], axis=0), axis=1).sum())

if __name__ == '__main__':
    for f in (711, 745):
        plane, rms = fit_plane(f)
        print(f'\n=== f={f}  plane n={np.round(plane[0],3)} d={plane[1]:.3f} rms={rms*100:.2f} cm')
        for b in 'LR':
            for route in ('S', 'C', 'P'):
                for click in ('centroid', 'mid'):
                    C, S = track(b, f, route, click, plane)
                    v = speed(S, 29); vc = speed(C, 29)
                    dS = S[30] - S[29]; rr = (np.linalg.norm(S[30]) - np.linalg.norm(S[29])) * 25
                    # physical: centre track, quadratic fit over capture 28..33 -> derivative at capture 30
                    ks = range(27, 33); c = np.array([cap(k) for k in ks]) / 25.0
                    vel = [np.polyfit(c, C[list(ks), j], 2) for j in range(3)]
                    vphys = np.linalg.norm([np.polyval(np.polyder(p), 1.2) for p in vel]) * 100
                    start = 21 if b == 'L' else 20
                    p_all = path(S, 0, N - 1); p_mov = path(S, start, N - 1)
                    p_fwd = path(S, 26 if b == 'L' else 21, 37); p_reb = path(S, 37, N - 1)
                    print(f'{b} {route} {click:8s} v1.2 label {v*100:6.1f} (centre {vc*100:6.1f}, radial {rr*100:+5.1f}) phys {vphys:6.1f} | '
                          f'path all {p_all*100:5.1f} moving {p_mov*100:5.1f} [fwd {p_fwd*100:5.1f} + reb {p_reb*100:4.1f}]  range29 {np.linalg.norm(S[29]):.3f}')
