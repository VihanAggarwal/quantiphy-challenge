# Label-style and physical values for the four motion rows, across renders, depth routes and clock variants.
# Route A (ballistic): fixed VP gravity | free gravity (per object) | joint shared free gravity; anchored at the stated range.
# Route B (apparent size): R(k) = R_stated * s(c15)/s(k), s = sqrt(area); raw and smoothed (linear fit of s over video 13-21).
import sys; sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0020/scripts')
from common import *
import ballfit as BF
from sizes import measure
T2 = json.load(open(D + 'track2.json'))
CUR = {('toy', 'v'): 274.92, ('jar', 'v'): 383.02, ('toy', 'disp'): 50.44, ('jar', 'disp'): 57.07}

def label_from_ranges(r, obj, R15, R16, R20, ks=(14, 15, 19), key='toy'):
    tr = T2[r][obj]
    P = [backproject(*tr[str(k)]['c'], R) for k, R in zip(ks, (R15, R16, R20))]
    return np.linalg.norm(P[1] - P[0]) * 2500, np.linalg.norm(P[2] - P[0]) * 100

rows = []
for clock, drops, ks in (('drop@c12', (12, 36), (14, 15, 19)), ('no-drop@c12', (36,), (15, 16, 20))):
    print('######## clock variant', clock, ' video frames for c15/c16/c20 =', ks)
    for obj, rng, off in (('jar', R_JAR, 0.035), ('toy', R_TOY, 0.04)):
        for r in 'osx':
            JK = list(range(15, 27)) if clock == 'drop@c12' else list(range(16, 27))
            TK = [15, 16, 17, 19, 20, 21, 22, 23, 24] if clock == 'drop@c12' else [16, 17, 19, 20, 21, 22, 23, 24]
            fk = JK if obj == 'jar' else TK
            res = {}
            for name, gfree in (('A-fixedg', False), ('A-freeg', True)):
                fz = BF.fit(r, obj, fk, rng=rng, off=off, gfree=gfree, drops=drops)
                Rc = np.linalg.norm(fz['pos']([0.6, 0.64, 0.8]), axis=1)
                v, d = label_from_ranges(r, obj, rng, Rc[1] - off, Rc[2] - off, ks)
                Q = fz['pos']([0.6, 0.64, 0.8])
                res[name] = (v, d, np.linalg.norm(fz['p'][3:6]) * 100, np.linalg.norm(Q[2] - Q[0]) * 100, Rc[1] - Rc[0], Rc[2] - Rc[0])
            # Route B: size
            ms = measure(r, obj, range(13, 22))
            kk = sorted(k for k in ms if not (obj == 'toy' and k == 18))
            s = {k: np.sqrt(ms[k]['area']) for k in kk}
            vb, db = label_from_ranges(r, obj, rng, rng * s[ks[0]] / s[ks[1]], rng * s[ks[0]] / s[ks[2]], ks)
            cf = np.polyfit(kk, [1 / s[k] for k in kk], 1)  # 1/s ~ range, linear in frame
            inv = lambda k: np.polyval(cf, k)
            vbs, dbs = label_from_ranges(r, obj, rng, rng * inv(ks[1]) / inv(ks[0]), rng * inv(ks[2]) / inv(ks[0]), ks)
            res['B-size-raw'] = (vb, db, np.nan, np.nan, rng * s[ks[0]] / s[ks[1]] - rng, rng * s[ks[0]] / s[ks[2]] - rng)
            res['B-size-smooth'] = (vbs, dbs, np.nan, np.nan, rng * inv(ks[1]) / inv(ks[0]) - rng, rng * inv(ks[2]) / inv(ks[0]) - rng)
            for name, (v, d, vi, dp, d16, d20) in res.items():
                print(f'{obj} {r} {name:14s} dR16 {d16*100:+5.1f}cm dR20 {d20*100:+5.1f}cm | label v {v:4.0f} (cur {CUR[(obj,"v")]:.0f}, {100*(CUR[(obj,"v")]/v-1):+4.0f}%) '
                      f'disp {d:5.1f} (cur {CUR[(obj,"disp")]:.1f}, {100*(CUR[(obj,"disp")]/d-1):+4.0f}%) | phys v_inst {vi:4.0f} disp {dp:5.1f}')
                rows.append(dict(clock=clock, obj=obj, r=r, route=name, v=v, disp=d, v_phys=vi, disp_phys=dp))
json.dump(rows, open(D + 'motion_table.json', 'w'), indent=0)
