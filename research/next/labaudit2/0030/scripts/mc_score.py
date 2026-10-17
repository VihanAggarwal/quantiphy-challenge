"""Monte Carlo of the forward-difference speed label at each asked time, and the expected item score (official MRA
thresholds) of candidate answers. Label: 25 * |(d(n+1)+e) u(c(n+1)+j1) - d(n) u(c(n)+j0)|, d(n) = stated (fixed),
e ~ N(0, sz) ToF noise at the unstated frame, j ~ N(0, 2 px) click jitter. E[d(n+1)] from several depth models."""
import numpy as np, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0030/scripts')
from depths import cap, unit, plane_pos, size_range, M, ANCH, R
import label_style as LS  # noqa (prints its table)

THR = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95])


def item(a, L):
    rel = np.abs(a - L) / L
    return (rel[:, None] < 1 - THR[None]).mean(1)


rng = np.random.default_rng(1)
N = 20000
cands = {0.2: [133.2, 140.85, 150, 160, 165, 170, 175, 180, 190],
         0.4: [122, 131.46, 132.86, 140, 150],
         0.6: [170, 182.07, 195, 210, 230],
         0.8: [170, 190, 210.2, 225, 240]}
for t in [0.2, 0.4, 0.6, 0.8]:
    n = int(round(t * 25)); d0 = ANCH[n]
    c0 = LS.click(n); c1 = LS.click(n + 1)
    i0, i1 = LS.idx(n), LS.idx(n + 1)
    # offset models: stated - route at n (and n10 for the two-anchor bias)
    models = {
        'plane persist': d0 + (LS.lfit(LS.rp, n, at=n + 1)[0] - LS.lfit(LS.rp, n)[0]),
        'size persist': d0 + (LS.lfit(LS.rs, n, at=n + 1)[0] - LS.lfit(LS.rs, n)[0]),
        'anchor-lin': LS.anchor_lin(n + 1),
    }
    # mean-bias model: route surface range at n+1 plus the mean stated-minus-route bias over all 4 anchors
    for nm, arr in [('plane', LS.rp), ('size', LS.rs)]:
        bias = np.mean([ANCH[a] - (LS.lfit(arr, a)[0] - R) for a in ANCH])
        models[f'{nm} meanbias'] = LS.lfit(arr, n, at=n + 1)[0] - R + bias
    print(f'\n=== t={t} (n{n}->n{n+1}), stated d(n)={d0}')
    for sz in [0.01, 0.02, 0.03]:
        for nm, d1 in models.items():
            j0 = rng.normal(0, 2, (N, 2)); j1 = rng.normal(0, 2, (N, 2))
            e = rng.normal(0, sz, N)
            U0 = np.array([unit(*(c0 + j)) for j in j0[:2000]]); U1 = np.array([unit(*(c1 + j)) for j in j1[:2000]])
            U0 = np.tile(U0, (N // 2000, 1)); U1 = np.tile(U1, (N // 2000, 1))
            L = np.linalg.norm((d1 + e)[:, None] * U1 - d0 * U0, axis=1) * 25 * 100
            sc = {a: item(np.full(N, a), L).mean() for a in cands[t]}
            print(f'  sz={sz:.2f} {nm:15s} d(n+1)={d1:.4f} label med {np.median(L):6.1f} mean {L.mean():6.1f} '
                  f'| E[score] ' + ' '.join(f'{a}:{s:.3f}' for a, s in sc.items()))
