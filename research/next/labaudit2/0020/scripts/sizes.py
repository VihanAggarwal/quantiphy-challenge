# Route B: apparent-size ranges. Per frame: blob area, width perpendicular to the motion direction (blur-free),
# min Feret width. Range(k) = R_stated(c15) * size(c15)/size(k), compared with the fit-predicted ranges (fixed / free gravity).
import sys; sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0020/scripts')
from common import *
from track2 import masks, comp_near
import ballfit as BF
T2 = json.load(open(D + 'track2.json'))

def perp_width(xs, ys, d):
    d = np.asarray(d, float); d = d / np.linalg.norm(d); n = np.array([-d[1], d[0]])
    pr = xs * n[0] + ys * n[1]
    return np.percentile(pr, 98) - np.percentile(pr, 2)

def feret_min(xs, ys):
    best = 1e9
    for a in np.linspace(0, np.pi, 90, endpoint=False):
        pr = xs * np.cos(a) + ys * np.sin(a)
        best = min(best, np.percentile(pr, 99) - np.percentile(pr, 1))
    return best

def measure(r, obj, ks):
    fr = frames(r); out = {}
    for k in ks:
        tr = T2[r][obj if obj != 'toyall' else 'toy']
        if str(k) not in tr: continue
        jar, yel, crown = masks(fr[k], r)
        m = jar if obj == 'jar' else (yel | crown if obj == 'toyall' else yel)
        res = comp_near(m, tr[str(k)]['c'])
        if res is None: continue
        xs, ys = res['pts']
        kp, kn = str(k - 1), str(k + 1)
        if kp in tr and kn in tr: d = np.subtract(tr[kn]['c'], tr[kp]['c'])
        elif kn in tr: d = np.subtract(tr[kn]['c'], tr[str(k)]['c'])
        else: d = np.subtract(tr[str(k)]['c'], tr[kp]['c'])
        out[k] = dict(area=len(xs), pw=perp_width(xs, ys, d), fmin=feret_min(xs, ys))
    return out

if __name__ == '__main__':
    for obj, rng, off, ks, fk in (('jar', R_JAR, 0.035, range(13, 28), list(range(15, 28))),
                                  ('toy', R_TOY, 0.04, range(13, 25), [15, 16, 17, 19, 20, 21, 22, 23, 24])):
        print('=====', obj)
        for r in ('x', 'o', 's'):
            ms = measure(r, obj, ks)
            fits = {g: BF.fit(r, obj, fk if not (obj == 'jar' and r == 's') else list(range(15, 27)), rng=rng, off=off, gfree=g) for g in (False, True)}
            ref = {key: np.mean([ms[k][key] for k in (14, 15, 16) if k in ms]) for key in ('area', 'pw', 'fmin')}
            # reference range = mean fit range over video 14-16 (anchored fits agree there to <1%)
            Rref = np.mean([np.linalg.norm(fits[False]['pos'](tau(np.array([k])))) for k in (14, 15, 16)]) - off
            print(f'render {r}  (sizes normalised to mean of video 14-16, Rref {Rref:.3f})')
            for k in sorted(ms):
                q = ms[k]
                Rs = [Rref * np.sqrt(ref['area'] / q['area']), Rref * ref['pw'] / q['pw'], Rref * ref['fmin'] / q['fmin']]
                Rf = [np.linalg.norm(fits[g]['pos'](tau(np.array([k]))) ) - off for g in (False, True)]
                print(f'  v{k:2d} c{int(cap_index(k)):2d} area {q["area"]:5d} pw {q["pw"]:5.1f} fmin {q["fmin"]:5.1f} | size-R area {Rs[0]:.2f} pw {Rs[1]:.2f} fmin {Rs[2]:.2f} | fit-R fixed {Rf[0]:.2f} free {Rf[1]:.2f}')
