"""Per-hop 3D ballistic fits of the ball centroid track on the 25 fps capture clock (drops before v12 and v36).
Gravity g=9.8 along the table normal (PnP plane, f=711/725/735). The fit's depth scale comes from gravity alone
(no stated range, no ball size). Reports, per hop: rms, range at each frame, implied ball diameter from the blob
minor axis, height of the centre above the table plane at the hop ends (bounce check)."""
import sys, json, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0037/scripts')
from common import OUT, cap, CX, CY

PL = json.load(open(OUT + '/plane.json'))
TR = json.load(open(OUT + '/track.json'))


def lsq(fun, x0, iters=300):
    x = np.array(x0, float); lam = 1e-3; f = fun(x); c = f @ f
    for _ in range(iters):
        J = np.empty((len(f), len(x)))
        for k in range(len(x)):
            h = 1e-6 * max(1.0, abs(x[k])); xp = x.copy(); xp[k] += h; J[:, k] = (fun(xp) - f) / h
        A = J.T @ J; g = J.T @ f
        while True:
            dx = -np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-12), g); fn = fun(x + dx); cn = fn @ fn
            if cn < c:
                x, f, c = x + dx, fn, cn; lam = max(lam / 3, 1e-9); break
            lam *= 4
            if lam > 1e9:
                break
        if lam > 1e9 or np.abs(dx).max() < 1e-12:
            break
    return x, f


def fit_hop(r, frames_, f=711, g=9.8, drops=(12, 36), tref=None, fixrange=None):
    pl = PL[str(f)]; nup = np.array(pl['n_up']); h = pl['h']
    tr = TR[r]
    if tref is None:
        tref = cap(frames_[0], drops)
    t = {n: (cap(n, drops) - tref) / 25.0 for n in frames_}

    def proj(X):
        return np.array([f * X[0] / X[2] + CX, f * X[1] / X[2] + CY])

    def pos(p, tt):
        return p[:3] + p[3:6] * tt - 0.5 * g * nup * tt * tt

    def res(p):
        out = []
        for n in frames_:
            out += list(proj(pos(p, t[n])) - [tr[str(n)]['u'], tr[str(n)]['v']])
        if fixrange is not None:
            n0, R0 = fixrange
            out.append(300 * (np.linalg.norm(pos(p, t[n0])) - R0))
        return np.array(out)
    n0 = frames_[0]
    u, v = tr[str(n0)]['u'], tr[str(n0)]['v']
    best = None
    for Z0 in (0.7, 1.0, 1.3):
        p0 = np.r_[Z0 * np.array([(u - CX) / f, (v - CY) / f, 1.0]), -0.5, 0.0, -0.3]
        p, fr = lsq(res, p0)
        c = fr @ fr
        if best is None or c < best[2]:
            best = (p, fr, c)
    p, fr, _ = best
    rr = fr[:2 * len(frames_)].reshape(-1, 2)
    return dict(p=p, rms=float(np.sqrt((rr ** 2).mean())), maxres=float(np.abs(rr).max()), t=t, tref=tref,
                pos=lambda tt: pos(p, tt), vel=lambda tt: p[3:6] - g * nup * tt, nup=nup, h=h, f=f)


if __name__ == '__main__':
    hops = {'B v20-27': list(range(20, 28)), 'B v21-27': list(range(21, 28)), 'B v21-26': list(range(21, 27)),
            'C v29-35': list(range(29, 36)), 'C v29-34': list(range(29, 35)), 'C v30-34': list(range(30, 35)),
            'D v37-42': list(range(37, 43)), 'A v13-18': list(range(13, 19))}
    for r in ('x', 's', 'o'):
        for f in (711, 735):
            print(f'=== render {r} f={f}')
            for name, fr_ in hops.items():
                if r == 'x' and 43 in fr_:
                    continue
                R = fit_hop(r, fr_, f=f)
                tr = TR[r]
                info = []
                for n in fr_:
                    X = R['pos'](R['t'][n]); rng = np.linalg.norm(X)
                    hgt = R['nup'] @ X + R['h']
                    d_cm = tr[str(n)]['emin'] * X[2] / f * 100
                    info.append(f'{n}:R{rng:.3f} h{hgt*100:4.1f} D{d_cm:3.1f}')
                # extrapolate to bounce: time when centre height = 2cm
                ts = np.linspace(-0.3, 0.6, 9001)
                hh = np.array([R['nup'] @ R['pos'](tt) + R['h'] for tt in ts])
                apex = ts[np.argmax(hh)]
                cross = ts[np.where(np.diff(np.sign(hh - 0.02)) != 0)[0]]
                cr = ' '.join(f'c{R["tref"] + c * 25:.1f}' for c in cross)
                print(f'{name}: rms {R["rms"]:.2f} max {R["maxres"]:.1f} | apex c{R["tref"] + apex * 25:.1f} hmax {hh.max()*100:.1f}cm | h=2cm at {cr}')
                print('    ' + ' '.join(info))
