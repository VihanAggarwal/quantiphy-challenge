# Route A: constant-g 3D fit of the image track (25 fps capture clock), with or without the stated-range anchor.
# Label-style values: clicked centre (measured blob centre) at capture 15/16/20 back-projected with a range
# (stated at c15; fit-predicted surface range at c16/c20), forward difference on the 25 fps clock.
import sys; sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0020/scripts')
from common import *
from lm import least_squares
T2 = json.load(open(D + 'track2.json'))
VP = (895.0, 1600.0)   # round-1 vertical vanishing point (wall seams, vent box)

def downdir(vp=VP, f=F):
    g = np.array([(vp[0] - CX) / f, (vp[1] - CY) / f, 1.0]); return g / np.linalg.norm(g)

def get_uv(r, obj, ks, key='c'):
    tr = T2[r][obj]
    ks = [k for k in ks if str(k) in tr]
    return ks, np.array([tr[str(k)][key] for k in ks])

def fit(r, obj, ks, rng=None, off=0.0, f=F, gfree=False, g=9.8, drops=(12, 36), wr=20.0, key='c', vp=VP):
    ks, uv = get_uv(r, obj, ks, key)
    t = tau(np.array(ks), drops)
    gd0 = downdir(vp, f)
    def gdir(p):
        if not gfree: return gd0
        q = np.array([p[6], p[7], 1.0]); return q / np.linalg.norm(q)
    def pos(p, tt):
        dt = (np.asarray(tt, float) - 0.6)[:, None]
        return p[:3] + p[3:6] * dt + 0.5 * g * dt ** 2 * gdir(p)
    def res(p):
        P = pos(p, t)
        rr = (project(P, f) - uv).ravel()
        if rng is not None: rr = np.r_[rr, wr * (np.linalg.norm(p[:3]) - (rng + off)) * 100]
        return rr
    u0 = np.interp(0.6, t, uv[:, 0]); v0 = np.interp(0.6, t, uv[:, 1])
    best = None
    for z in (1.5, 2.0, 2.5, 3.0, 3.5):
        for vz in (-2, 0, 2):
            p0 = np.r_[z * ray(u0, v0, f), 0, -2, vz]
            if gfree: p0 = np.r_[p0, gd0[0] / gd0[2], gd0[1] / gd0[2]]
            s = least_squares(res, p0)
            if best is None or s.cost < best.cost: best = s
    p = best.x
    P = pos(p, t)
    rms = np.sqrt(np.mean(np.sum((project(P, f) - uv) ** 2, 1)))
    return dict(p=p, pos=lambda tt: pos(p, tt), rms=rms, gd=gdir(p), ks=ks, uv=uv)

def label_style(r, obj, fitres, rng_stated, off, f=F, drops=(12, 36), k15=14, k16=15, k20=19, key='c'):
    """clicked centre = measured blob centre at video k; range at c15 = stated, at c16/c20 = fit centre range - off,
    optionally shifted so the fit range at c15 matches the stated (delta route)."""
    tr = T2[r][obj]
    pos = fitres['pos']
    t15, t16, t20 = 0.60, 0.64, 0.80
    Rc = np.linalg.norm(pos([t15, t16, t20]), axis=1)          # fit centre ranges
    out = {}
    for mode in ('abs', 'delta'):
        if mode == 'abs':
            R = [rng_stated, Rc[1] - off, Rc[2] - off]
        else:
            R = [rng_stated, rng_stated + (Rc[1] - Rc[0]), rng_stated + (Rc[2] - Rc[0])]
        P = [backproject(*tr[str(k)][key], R[i], f) for i, k in enumerate((k15, k16, k20))]
        out[mode] = dict(v=np.linalg.norm(P[1] - P[0]) * 25 * 100, disp=np.linalg.norm(P[2] - P[0]) * 100,
                         R16=R[1], R20=R[2])
    Q = pos([t15, t16, t20])
    out['phys'] = dict(v_inst=np.linalg.norm(fitres['p'][3:6]) * 100, v_fd=np.linalg.norm(Q[1] - Q[0]) * 2500,
                       disp=np.linalg.norm(Q[2] - Q[0]) * 100, R15=Rc[0], R16=Rc[1], R20=Rc[2])
    return out

if __name__ == '__main__':
    JK = {'o': list(range(15, 28)), 's': list(range(15, 27)), 'x': list(range(15, 28))}
    TK = [15, 16, 17, 19, 20, 21, 22, 23, 24]
    rows = []
    for obj, rng, off in (('jar', R_JAR, 0.035), ('toy', R_TOY, 0.04)):
        for r in 'osx':
            ks = JK[r] if obj == 'jar' else TK
            for gfree in (False, True):
                for anch in (True, False):
                    for f in (711.0, 722.0):
                        fr = fit(r, obj, ks, rng=rng if anch else None, off=off, f=f, gfree=gfree)
                        ls = label_style(r, obj, fr, rng, off, f=f)
                        rows.append((obj, r, gfree, anch, f, fr, ls))
                        ph = ls['phys']
                        print(f"{obj} {r} gfree={int(gfree)} anch={int(anch)} f={f:.0f} rms={fr['rms']:.2f} gd={np.round(fr['gd'],2)} "
                              f"R15/16/20={ph['R15']:.3f}/{ph['R16']:.3f}/{ph['R20']:.3f} | phys v_inst {ph['v_inst']:.0f} v_fd {ph['v_fd']:.0f} disp {ph['disp']:.1f} | "
                              f"label abs v {ls['abs']['v']:.0f} disp {ls['abs']['disp']:.1f} | delta v {ls['delta']['v']:.0f} disp {ls['delta']['disp']:.1f}")
