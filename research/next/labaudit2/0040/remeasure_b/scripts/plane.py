import numpy as np, json
P = json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0040/remeasure_b/pnp.json'))
def plane(f):
    d = P['%d_76' % f]; R = np.array(d['R']); t = np.array(d['t'])
    n = R[:, 2]; d0 = n @ t   # plane: n.X = d0 (cm)
    return n, d0
def ray_plane(u, v, f, h=0.0):
    n, d0 = plane(f)
    r = np.array([(u - 640) / f, (v - 360) / f, 1.0])
    # plane offset by height h along table normal (toward camera side). normal sign: camera side?
    # camera at origin: n.0 = 0; table plane n.X=d0. points above table (toward camera) have n.X between 0 and d0
    s = np.sign(d0)
    lam = (d0 - s * h) / (n @ r)
    return lam * r
if __name__ == '__main__':
    pts = dict(card=(563, 541), tower_base=(688, 497), cup_base=(776, 503), tape_base=(590, 484), jar_base=(511, 495))
    for f in [711, 740]:
        n, d0 = plane(f)
        print('f', f, 'normal', n.round(4), 'cam height above table %.2f cm' % abs(d0))
        for k, (u, v) in pts.items():
            X = ray_plane(u, v, f)
            print('   %-10s Z %.1f  range %.1f cm' % (k, X[2], np.linalg.norm(X)))
