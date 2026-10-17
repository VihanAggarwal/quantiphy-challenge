"""Label-style emulation for v(1.6) of both balls (capture n40 -> n41 = video k38 -> k39).
Q40 = D40 * ray(click40), Q41 = (D40 + s*dR + noise) * ray(click41); clicks = measured centres + N(0, sx px).
D40 = stated reading of the object whose depth the label uses (hypothesis):
  H1 text-only swap: tennis label uses tennis clicks + 0.994 series; white uses white clicks + 1.19 series
  H2 identity swap : 'tennis' label = white clicks + 1.19 series; 'white' label = tennis clicks + 0.994 series
  H0 depth-only swap: tennis clicks + white's 1.19 series (dR of white); white clicks + tennis's 0.994 series
dR = my per-frame centre-range change (f=711) times ToF scale s (1.00 / 1.065); physical uncertainty of dR
drawn uniform over the route spread.  sigma_z on the next-frame reading only (D40 is the stated value), or
on both (unanchored).  Reports deterministic label, MC median, MRA-optimal answer, expected MRA of answers.
"""
import numpy as np, json
B = '/home/user/quantiphy-challenge/research/next/labaudit2/0031/'
co = json.load(open(B + 'chords_o.json')); cx = json.load(open(B + 'chords_x.json'))
THR = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95])


def mra(pred, gt):
    rel = np.abs(pred - gt) / gt
    return (rel[..., None] < 1 - THR).mean(-1)


def centre(ball, k):
    a, b = co[k][ball], cx[k][ball]
    return np.array([0.5 * (a['xc'] + b['xc']), 0.5 * (a['yc_fit'] + b['yc_fit'])])


def rays(uv, F):
    v = np.concatenate([(uv - [640, 360]) / F, np.ones(uv.shape[:-1] + (1,))], -1)
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


# per-frame radial change of the surface range (cm per capture frame), f=711 routes (speed.py):
# tennis -2.04..-2.52 (size and plane fits), white -1.51..-1.95
DR = {'T': (-2.52, -2.04), 'W': (-1.95, -1.51)}
STATED = {'T': 99.4, 'W': 119.0}   # swapped stated readings = physical object readings
rng = np.random.default_rng(1)
N = 40000
answers = {'T': [45, 47, 50, 55, 58, 60, 62, 65, 68, 71.84, 77.52], 'W': [45.6, 46.6, 47.76, 50, 55, 58, 60, 62, 65]}
res = {}
for hyp in ('H1', 'H2', 'H0'):
    for q in ('T', 'W'):
        if hyp == 'H1': clk, dser = q, q
        elif hyp == 'H2': clk = dser = ('W' if q == 'T' else 'T')
        else: clk, dser = q, ('W' if q == 'T' else 'T')
        c40, c41 = centre(clk, 38), centre(clk, 39)
        for s in (1.0, 1.065):
            for F in (711.0, 760.0):
                for sz, both in ((0.0, False), (1.0, False), (2.0, False), (2.0, True)):
                    sx = 2.0
                    u40 = rays(c40 + rng.normal(0, sx, (N, 2)), F)
                    u41 = rays(c41 + rng.normal(0, sx, (N, 2)), F)
                    dR = rng.uniform(*DR[dser], N) * s
                    D40 = STATED[dser] + (rng.normal(0, sz, N) if both else np.zeros(N))
                    D41 = STATED[dser] + dR + rng.normal(0, sz, N)
                    L = np.linalg.norm(D41[:, None] * u41 - D40[:, None] * u40, axis=1) * 25
                    # deterministic
                    ud40, ud41 = rays(c40[None], F)[0], rays(c41[None], F)[0]
                    det = np.linalg.norm((STATED[dser] + np.mean(DR[dser]) * s) * ud41 - STATED[dser] * ud40) * 25
                    grid = np.arange(30, 120.1, 0.5)
                    sc = np.array([mra(g, L).mean() for g in grid])
                    best = grid[np.argmax(sc)]
                    ex = {a: float(mra(a, L).mean()) for a in answers[q]}
                    key = f'{hyp}_{q}_s{s}_F{int(F)}_sz{sz}_{"both" if both else "next"}'
                    res[key] = dict(det=float(det), med=float(np.median(L)), best=float(best), best_sc=float(sc.max()), ex=ex)
                    print('%-34s det=%5.1f med=%5.1f p25=%5.1f p75=%5.1f best=%5.1f (%.3f) | %s' % (
                        key, det, np.median(L), np.percentile(L, 25), np.percentile(L, 75), best, sc.max(),
                        ' '.join('%g:%.3f' % (a, v) for a, v in ex.items())))
json.dump(res, open(B + 'mc.json', 'w'), indent=0)
