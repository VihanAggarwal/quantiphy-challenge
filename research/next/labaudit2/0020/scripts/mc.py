# Label-noise Monte Carlo for the four motion rows: click jitter (px) on each click, ToF noise (cm) on the unstated
# readings (c16, c20), depth route drawn 50/50 from fixed-VP / free-gravity ballistic fits (all three renders).
# Reports the label distribution, expected score of the current answer and the score-optimal constant.
import sys; sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0020/scripts')
from common import *
import ballfit as BF
T2 = json.load(open(D + 'track2.json'))
CUR = {('toy', 'v'): 274.92, ('jar', 'v'): 383.02, ('toy', 'disp'): 50.44, ('jar', 'disp'): 57.07}
rng_ = np.random.default_rng(0)

def score(pred, y):
    e = np.abs(pred - y) / np.abs(y)
    return np.where(e < 0.05, 1.0, np.clip(1 - e, 0, 1))

routes = {}
for obj, rng, off, fk in (('jar', R_JAR, 0.035, list(range(15, 27))), ('toy', R_TOY, 0.04, [15, 16, 17, 19, 20, 21, 22, 23, 24])):
    routes[obj] = []
    for r in 'osx':
        for g in (False, True):
            fz = BF.fit(r, obj, fk, rng=rng, off=off, gfree=g)
            Rc = np.linalg.norm(fz['pos']([0.6, 0.64, 0.8]), axis=1)
            uv = [np.array(T2[r][obj][str(k)]['c']) for k in (14, 15, 19)]
            routes[obj].append((uv, rng, Rc[1] - off, Rc[2] - off))

for sz_px, sz_cm in ((2.0, 1.0), (3.0, 2.0), (3.0, 3.0)):
    print(f'--- click sd {sz_px}px, ToF sd {sz_cm}cm')
    for obj in ('jar', 'toy'):
        N = 20000
        vs = []; ds = []
        for i in range(N):
            uv, R15, R16, R20 = routes[obj][rng_.integers(len(routes[obj]))]
            c = [u + rng_.normal(0, sz_px, 2) for u in uv]
            P15 = backproject(*c[0], R15)
            P16 = backproject(*c[1], R16 + rng_.normal(0, sz_cm / 100))
            P20 = backproject(*c[2], R20 + rng_.normal(0, sz_cm / 100))
            vs.append(np.linalg.norm(P16 - P15) * 2500); ds.append(np.linalg.norm(P20 - P15) * 100)
        for q, arr in (('v', np.array(vs)), ('disp', np.array(ds))):
            grid = np.linspace(np.percentile(arr, 2), np.percentile(arr, 98), 300)
            es = [score(g, arr).mean() for g in grid]
            best = grid[int(np.argmax(es))]
            cur = CUR[(obj, q)]
            print(f'{obj} {q:4s} label p10/p50/p90 {np.percentile(arr,10):.1f}/{np.median(arr):.1f}/{np.percentile(arr,90):.1f} | '
                  f'current {cur:.1f} E[score] {score(cur, arr).mean():.3f} | optimal {best:.1f} E[score] {max(es):.3f}')
