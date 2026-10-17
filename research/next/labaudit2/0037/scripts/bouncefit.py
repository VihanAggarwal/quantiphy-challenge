"""Joint piecewise-ballistic 3D fit with bounce points ON the table plane (ball centre 2 cm above the top).
Parameters: for each bounce k: capture time t_k, and the 3D centre Q_k constrained to the plane (2 params: a point
on the plane via the image ray of a pixel (bu,bv)). Between bounces k and k+1 the path is ballistic with gravity
g along -n_up: X(t) = Q_k + (Q_k1-Q_k)*s + 0.5*g*n_up*(t-t_k)*(t_k1-t), s=(t-t_k)/(t_k1-t_k).
Scale is fixed by the plane (h from the table PnP) AND by gravity; variant 'gfree' lets g float as a check.
Data: tracked centroids of clean in-flight frames (bounce frames and occluded frames left out).
Reports bounce times/positions, g, rms, velocity and range at c25 (t=1.0 s), c35 (t=1.4 s) and label-style FDs."""
import sys, json, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0037/scripts')
from common import OUT, cap, CX, CY
from ballistic import lsq

PL = json.load(open(OUT + '/plane.json'))
TR = json.load(open(OUT + '/track.json'))
HOPS = [list(range(21, 28)), list(range(29, 36)), list(range(37, 43))]   # B, C, D (between bounces 1..4)


def run(r, f=711, gfree=False, hops=HOPS, drop_frames=(), R_ball=0.02, verbose=True):
    pl = PL[str(f)]; nup = np.array(pl['n_up']); h = pl['h']
    tr = TR[r]
    nb = len(hops) + 1

    def Q(bu, bv):     # centre on plane h=R_ball for image point (bu,bv)
        ray = np.array([(bu - CX) / f, (bv - CY) / f, 1.0])
        s = (-h + R_ball) / (nup @ ray)
        return s * ray

    def unpack(p):
        ts = p[:nb]; B = p[nb:3 * nb].reshape(nb, 2)
        g = p[3 * nb] if gfree else 9.8
        return ts, [Q(*b) for b in B], g

    def X(p, t):
        ts, Qs, g = unpack(p)
        k = int(np.clip(np.searchsorted(ts, t) - 1, 0, nb - 2))
        T = ts[k + 1] - ts[k]; s = (t - ts[k]) / T
        return Qs[k] + (Qs[k + 1] - Qs[k]) * s + 0.5 * g * nup * (t - ts[k]) * (ts[k + 1] - t) / 625.0  # t in frames

    def proj(Xc):
        return np.array([f * Xc[0] / Xc[2] + CX, f * Xc[1] / Xc[2] + CY])

    obs = [(cap(n), n) for hop in hops for n in hop if n not in drop_frames]

    def res(p):
        out = []
        for c, n in obs:
            out += list(proj(X(p, c)) - [tr[str(n)]['u'], tr[str(n)]['v']])
        return np.array(out)
    # init: bounce times and pixels from the track
    t0 = [20.4, 29.3, 37.5, 45.4][:nb]
    b0 = [(705, 440), (583, 460), (445, 462), (330, 480)][:nb]
    p0 = np.r_[t0, np.array(b0, float).ravel()] if not gfree else np.r_[t0, np.array(b0, float).ravel(), 9.8]
    p, fr = lsq(res, p0, iters=500)
    rr = fr.reshape(-1, 2)
    ts, Qs, g = unpack(p)
    out = dict(rms=float(np.sqrt((rr ** 2).mean())), maxres=float(np.abs(rr).max()), g=float(g), ts=ts.tolist(),
               X=lambda t: X(p, t), Qs=Qs, nup=nup, h=h)

    def V(t, dt=1e-4):
        return (X(p, t + dt) - X(p, t - dt)) / (2 * dt) * 25.0   # m/s (t in capture frames)
    out['V'] = V
    if verbose:
        print(f'  render {r} f={f} gfree={gfree} drop={drop_frames}: rms {out["rms"]:.2f} max {out["maxres"]:.2f} g={g:.2f}')
        print('   bounces: ' + ' '.join(f'c{t:.2f}:R{np.linalg.norm(q):.3f}' for t, q in zip(ts, Qs)))
        for k in range(nb - 1):
            T = (ts[k + 1] - ts[k]) / 25
            vh = (Qs[k + 1] - Qs[k]) / T
            Rk = np.linalg.norm(Qs[k]); Rk1 = np.linalg.norm(Qs[k + 1])
            print(f'   hop {k}: T={T:.3f}s horiz speed {np.linalg.norm(vh)*100:.1f} cm/s, mean range-rate {(Rk1-Rk)/T*100:+.1f} cm/s, apex height {g*T*T/8*100+2:.1f} cm')
        for tc in (25, 35):
            Xc = X(p, tc); v = V(tc); rhat = Xc / np.linalg.norm(Xc)
            fd = np.linalg.norm(X(p, tc + 1) - X(p, tc)) * 25 * 100
            print(f'   c{tc}: range {np.linalg.norm(Xc):.3f} |V| {np.linalg.norm(v)*100:.1f} cm/s (radial {v@rhat*100:+.1f}, vert {v@nup*100:+.1f}) '
                  f'FD c{tc}->c{tc+1} {fd:.1f} cm/s; range c{tc+1} {np.linalg.norm(X(p, tc+1)):.3f}')
    return out


if __name__ == '__main__':
    for r in ('x', 's'):
        for f in (711, 735):
            run(r, f)
            run(r, f, gfree=True)
            run(r, f, drop_frames=(29, 35))
            run(r, f, drop_frames=(21, 29, 35, 42))
