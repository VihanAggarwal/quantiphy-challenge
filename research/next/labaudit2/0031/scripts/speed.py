"""Physical and label-style speeds at t=1.6 s (capture n=40, video k=38) for both balls.
Physical: polynomial fits of 3D position (size route, plane route) vs capture time, derivative at n=40,
and the fitted forward difference n40->n41.
Label-style: click centres at k=38 and k=39 (measured), range at k=38 = stated value under a hypothesis,
range at k=39 = stated + (surface-range change over n40->41 from the smooth route); also MC with click
jitter 2 px and ToF noise 2 cm.
"""
import numpy as np, json, sys
B = '/home/user/quantiphy-challenge/research/next/labaudit2/0031/'
F = float(sys.argv[1]) if len(sys.argv) > 1 else 711.0
R = json.load(open(B + f'routes_f{int(F)}.json'))
pp = np.array([640., 360.])


def ray(x, y):
    v = np.array([(x - pp[0]) / F, (y - pp[1]) / F, 1.0]); return v / np.linalg.norm(v)


rad = {'T': 3.35, 'W': 2.0}
res = {}
for ball, win in (('T', [(29, 44), (32, 44), (34, 43), (30, 42)]), ('W', [(29, 50), (32, 50), (34, 46), (30, 48)])):
    rows = R[ball]
    n = np.array([r['n'] for r in rows]); k = np.array([r['k'] for r in rows])
    print('=== ball', ball)
    for key in ('Ps', 'Pp'):
        P = np.array([r[key] for r in rows])
        for (a, b) in win:
            s = (n >= a) & (n <= b)
            for deg in (1, 2):
                if deg == 1 and (b - a) > 13: continue
                cs = [np.polyfit(n[s] / 25, P[s, j], deg) for j in range(3)]
                v = np.array([np.polyval(np.polyder(c), 1.6) for c in cs])
                fd = np.array([np.polyval(c, 41 / 25) - np.polyval(c, 40 / 25) for c in cs]) * 25
                Rfit = lambda t: np.linalg.norm([np.polyval(c, t) for c in cs])
                dR = (Rfit(41 / 25) - Rfit(40 / 25))
                print('  %s n%02d-%02d deg%d  |v(1.6)|=%.1f  v=%s  fwd=%.1f  R(1.6)=%.1f  dR/frame=%.2f' % (
                    key, a, b, deg, np.linalg.norm(v), v.round(1), np.linalg.norm(fd), Rfit(1.6), dR))
                res.setdefault(ball, []).append(dict(route=key, win=(a, b), deg=deg, v=float(np.linalg.norm(v)),
                                                     fwd=float(np.linalg.norm(fd)), R=float(Rfit(1.6)), dR=float(dR), vvec=v.tolist()))
    # raw chord between frames
    for key in ('Ps', 'Pp'):
        P = {r['k']: np.array(r[key]) for r in rows}
        for (a, b) in ((38, 39), (37, 39), (37, 40), (36, 40), (36, 41), (35, 41), (34, 42)):
            if a in P and b in P:
                dn = (b + (b >= 36) + (b >= 12)) - (a + (a >= 36) + (a >= 12))
                print('  raw %s k%d->k%d (dn=%d): %.1f' % (key, a, b, dn, np.linalg.norm(P[b] - P[a]) * 25 / dn))
json.dump(res, open(B + f'speed_f{int(F)}.json', 'w'))
