# Test: does a rolling-shutter time offset per image row (t = tau + Tr*(v-360)/720) reconcile the VP gravity direction
# with the tracks? Fixed VP gravity, free Tr, optional anchor. Joint jar + toy fit (shared Tr).
import sys; sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0020/scripts')
from common import *
from lm import least_squares
import ballfit as BF
JK = list(range(15, 27)); TK = [15, 16, 17, 19, 20, 21, 22, 23, 24]

def joint_rs(r, anchor=True, Tr=None, f=F, vp=BF.VP, gfree=False, gmag=9.8):
    kj, uj = BF.get_uv(r, 'jar', JK); kt, ut = BF.get_uv(r, 'toy', TK)
    tj0 = tau(np.array(kj)); tt0 = tau(np.array(kt))
    gd0 = BF.downdir(vp, f)
    def unpack(p):
        tr = p[12] if Tr is None else Tr
        g = gd0 if not gfree else (lambda q: q / np.linalg.norm(q))(np.array([p[13], p[14], 1.0]))
        return tr, g
    def pos(p0, v0, g, t):
        dt = (np.asarray(t, float) - 0.6)[:, None]; return p0 + v0 * dt + 0.5 * gmag * dt ** 2 * g
    def res(p):
        tr, g = unpack(p)
        tj = tj0 + tr * (uj[:, 1] - 360) / 720; tt = tt0 + tr * (ut[:, 1] - 360) / 720
        a = (project(pos(p[0:3], p[3:6], g, tj), f) - uj).ravel()
        b = (project(pos(p[6:9], p[9:12], g, tt), f) - ut).ravel()
        rr = np.r_[a, b]
        if anchor: rr = np.r_[rr, 20 * (np.linalg.norm(p[0:3]) - R_JAR - .035) * 100, 20 * (np.linalg.norm(p[6:9]) - R_TOY - .04) * 100]
        return rr
    best = None
    for tr0 in (0.0, 0.02, -0.02):
        p0 = np.r_[2.0 * ray(*uj[0]), 0, -2, 1, 2.6 * ray(*ut[0]), -1, 0, -2, tr0]
        if gfree: p0 = np.r_[p0, gd0[0] / gd0[2], gd0[1] / gd0[2]]
        s = least_squares(res, p0)
        if best is None or s.cost < best.cost: best = s
    p = best.x; tr, g = unpack(p)
    n = 2 * (len(kj) + len(kt))
    rms = np.sqrt(np.sum(best.fun[:n] ** 2) / (n / 2))
    # positions at nominal capture times (the ToF/click instant for the image centre row; the label uses the image as is)
    Qj = pos(p[0:3], p[3:6], g, [0.6, 0.64, 0.8]); Qt = pos(p[6:9], p[9:12], g, [0.6, 0.64, 0.8])
    return dict(Tr=tr, g=g, rms=rms, Qj=Qj, Qt=Qt, p=p)

if __name__ == '__main__':
    for r in 'osx':
        for anchor in (True, False):
            for gfree in (False, True):
                q = joint_rs(r, anchor=anchor, gfree=gfree)
                Rj = np.linalg.norm(q['Qj'], axis=1); Rt = np.linalg.norm(q['Qt'], axis=1)
                print(f"{r} anchor={int(anchor)} gfree={int(gfree)} Tr={q['Tr']*1000:+.1f}ms g={np.round(q['g'],3)} rms {q['rms']:.2f} | "
                      f"jar R {Rj[0]:.3f}/{Rj[1]:.3f}/{Rj[2]:.3f} v {np.linalg.norm(q['Qj'][1]-q['Qj'][0])*2500:.0f} disp {np.linalg.norm(q['Qj'][2]-q['Qj'][0])*100:.1f} | "
                      f"toy R {Rt[0]:.3f}/{Rt[1]:.3f}/{Rt[2]:.3f} v {np.linalg.norm(q['Qt'][1]-q['Qt'][0])*2500:.0f} disp {np.linalg.norm(q['Qt'][2]-q['Qt'][0])*100:.1f}")
        for Tr in (0.0,):
            q = joint_rs(r, anchor=False, Tr=Tr)
            Rj = np.linalg.norm(q['Qj'], axis=1); Rt = np.linalg.norm(q['Qt'], axis=1)
            print(f"{r} anchor=0 fixed Tr=0 rms {q['rms']:.2f} jar R {Rj[0]:.3f} toy R {Rt[0]:.3f}")
