"""Label-noise Monte Carlo for the two ping-pong speed labels of event 0037 (shared by o/s/x).
Noise-free click pairs (pixel, surface range) come from motion.py's routes; the annotator adds click jitter
sigma_px (px) and ToF noise sigma_z (m) per click; label = |P1-P0|*25. Expected MRA of candidate answers
(QuantiPhy thresholds 0.5..0.95) per scenario, plus the MRA-optimal constant."""
import sys, json, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0037/scripts')
from common import OUT, ray, F, CX, CY
THR = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95])


def mra(pred, gt):
    rel = np.abs(pred - gt) / gt
    return (rel[..., None] < 1 - THR).mean(-1)


def labels(c0, R0, c1, R1, spx, sz, n=20000, seed=0):
    rng = np.random.default_rng(seed)
    out = []
    P = []
    for (u, v), R in ((c0, R0), (c1, R1)):
        uu = u + rng.normal(0, spx, n); vv = v + rng.normal(0, spx, n); rr = R + rng.normal(0, sz, n)
        d = np.stack([(uu - CX) / F, (vv - CY) / F, np.ones(n)], 1)
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        P.append(d * rr[:, None])
    return np.linalg.norm(P[1] - P[0], axis=1) * 25 * 100


SC = {
    't1.0': {  # (click v24, R_surf, click v25, R_surf)
        'size within-hop B (-15 cm/s)': ((639.5, 351.5), 1.055, (626.3, 357.7), 1.055 - 0.0060),
        'size line B-D / hop-B fit v21-27 (-38)': ((639.5, 351.5), 1.055, (626.3, 357.7), 1.055 - 0.0152),
        'joint bounce fit f735 (-50)': ((639.5, 351.5), 1.055, (626.3, 357.7), 1.055 - 0.0200),
        'hop-B fit v21-28 (-57)': ((639.5, 351.5), 1.055, (626.3, 357.7), 1.055 - 0.0227),
    },
    't1.4': {
        'tracked v35, size range .906 (-38)': ((498.9, 376.9), 0.906, (485.8, 394.2), 0.906 - 0.0152),
        'whole-ball v35, size range .906 (-38)': ((498.9, 376.9), 0.906, (483.2, 401.0), 0.906 - 0.0152),
        'tracked v35, gravity range .979 (-27)': ((498.9, 376.9), 0.979, (485.8, 394.2), 0.979 - 0.0108),
        'whole-ball v35, gravity range .979 (-27)': ((498.9, 376.9), 0.979, (483.2, 401.0), 0.979 - 0.0108),
    }}
CAND = {'t1.0': [48.5, 58.1, 59.0, 65, 70, 75, 80, 85], 't1.4': [55.1, 75.9, 76.6, 85, 90, 95, 100, 110]}

if __name__ == '__main__':
    for t, scs in SC.items():
        print(f'===== {t}; candidates {CAND[t]}')
        agg = {}
        for name, (c0, R0, c1, R1) in scs.items():
            nf = labels(c0, R0, c1, R1, 0, 0, n=1)[0]
            for spx in (2.0,):
                for sz in (0.0, 0.01, 0.02, 0.03):
                    L = labels(c0, R0, c1, R1, spx, sz)
                    sc = [mra(a, L).mean() for a in CAND[t]]
                    grid = np.arange(30, 200, 1.0)
                    g = np.array([mra(a, L).mean() for a in grid])
                    agg.setdefault(sz, []).append(np.array(sc))
                    print(f'{name:48s} noise-free {nf:5.1f} | px {spx} sz {sz:.2f}: median label {np.median(L):5.1f} | '
                          + ' '.join(f'{a}:{s:.2f}' for a, s in zip(CAND[t], sc)) + f' | best {grid[g.argmax()]:.0f} ({g.max():.2f})')
        print('mean over scenarios:')
        for sz, v in agg.items():
            m = np.mean(v, axis=0)
            print(f'  sz {sz:.2f}: ' + ' '.join(f'{a}:{s:.2f}' for a, s in zip(CAND[t], m)))
