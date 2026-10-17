"""3D routes for both balls of captured_0031 on the 25 fps capture clock.
 size route : centre range from apparent diameter (tennis 6.7, white D_w), along the centre ray
 plane route: ray through centre pixel meets plane at height r above the table (PnP pose, W=60.3 front edge)
Capture index n = k + (k>=12) + (k>=36).  t = 1.6 s -> n = 40 -> video k = 38; forward step 38 -> 39.
"""
import numpy as np, json, sys
B = '/home/user/quantiphy-challenge/research/next/labaudit2/0031/'
co = json.load(open(B + 'chords_o.json')); cx_ = json.load(open(B + 'chords_x.json'))
pose = json.load(open(B + 'pose.json'))
cap = lambda k: k + (k >= 12) + (k >= 36)
F = float(sys.argv[1]) if len(sys.argv) > 1 else 711.0
DW = float(sys.argv[2]) if len(sys.argv) > 2 else 4.0
P0 = pose[f'{int(F)}_60.3'] if f'{int(F)}_60.3' in pose else pose['711_60.3']
Rm = np.array(P0['R']); tv = np.array(P0['t'])
n_up = Rm @ np.array([0, 0, 1.]); d0 = n_up @ tv   # n.X = d0 on table top (cm)
pp = np.array([640., 360.])


def ray(x, y):
    v = np.array([(x - pp[0]) / F, (y - pp[1]) / F, 1.0]); return v / np.linalg.norm(v)


def get(ball, k, which='avg'):
    a = co[k].get(ball); b = cx_[k].get(ball)
    if which == 'o' or b is None: b = a
    if which == 'x' or a is None: a = b
    if a is None: return None
    x = 0.5 * (a['xc'] + b['xc']); y = 0.5 * (a['yc_fit'] + b['yc_fit'])
    d = 0.25 * (a['d_circ'] + a['d_quad'] + b['d_circ'] + b['d_quad'])
    return x, y, d


rad = {'T': 3.35, 'W': DW / 2}
out = {}
for ball in ('T', 'W'):
    kk = range(14, 43) if ball == 'T' else range(14, 49)
    rows = []
    for k in kk:
        g = get(ball, k)
        if g is None: continue
        x, y, d = g
        u = ray(x, y)
        Rc_size = rad[ball] / np.sin(np.arctan(d / 2 / F))
        s = (d0 + rad[ball]) / (n_up @ u)
        rows.append(dict(k=k, n=int(cap(k)), x=x, y=y, d=d, Rs=Rc_size, Rp=s, Ps=(Rc_size * u).tolist(), Pp=(s * u).tolist()))
    out[ball] = rows

json.dump(out, open(B + f'routes_f{int(F)}.json', 'w'))
print('F', F, 'plane d0 %.2f n %s' % (d0, n_up.round(4)))
for ball in ('T', 'W'):
    print('ball', ball)
    for r in out[ball]:
        if r['k'] >= 28:
            print('  k=%2d n=%2d x=%.1f y=%.1f d=%.2f  R_size=%.1f  R_plane=%.1f  ratio=%.3f' % (r['k'], r['n'], r['x'], r['y'], r['d'], r['Rs'], r['Rp'], r['Rp'] / r['Rs']))
