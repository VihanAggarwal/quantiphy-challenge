"""MRA-optimal answer for the v(1.5)/v(1.4)/path rows under the label-process noise model of research/labnoise
(click jitter sigma_px, ToF range noise sigma_z per click, forward difference at 25 fps), using MY geometry
(3D points from motion.py, anchor ranges) and a log-normal uncertainty of my own physical value (sig_A)."""
import sys, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0040/scripts')
sys.path.insert(0, '/home/user/quantiphy-challenge/research/labnoise')
import motion as M
import labmodel as LM
THR = LM.THR
def mra(pred, gt):
    rel = np.abs(pred - gt) / gt; return (rel[..., None] < 1 - THR).mean(-1)
tr = M.load('x', 'caps')
P = {n: M.rng_anchor(M.cap(n)) * M.ray(tr[n]['u'], tr[n]['v']) for n in tr}
rng = np.random.default_rng(1)
def run(name, pts, current, sig_A=0.08, n=20000):
    """pts: list of 3D points at consecutive capture frames (true path); label = sum of noisy segment lengths
    (x25 for a single-segment speed)."""
    pts = np.array(pts); speed = len(pts) == 2
    base = np.linalg.norm(np.diff(pts, axis=0), axis=1).sum() * (25 if speed else 1) * 100
    print(f'== {name}: noiseless label-style {base:.1f}; current {current}')
    for sz in (0.0, 0.01, 0.02, 0.03):
        k = np.exp(rng.normal(0, sig_A, n))                          # my own scale error
        Q = pts[None] * 1.0
        Qk = pts[0] + k[:, None, None] * (pts - pts[0])[None]
        L = LM.path_labels_s(Qk, 2.0, sz, seed=int(sz * 1000) + 3) * (25 if speed else 1) * 100
        grid = np.arange(0.5, 2.0, 0.005) * base
        sc = np.array([mra(g, L).mean() for g in grid])
        best = grid[np.argmax(sc)]
        print(f'   sigma_z={sz:.2f}: label median {np.median(L):6.1f} mean {L.mean():6.1f}; MRA-opt answer {best:6.1f} '
              f'(E[MRA] {sc.max():.3f}); E[MRA] of current {mra(current, L).mean():.3f}; of noiseless {mra(base, L).mean():.3f}')
run('v(1.5) c38->39 (video 36->37)', [P[36], P[37]], 106.076)
run('v(1.4) c35->36 (video 34->35)', [P[34], P[35]], 106.076)
run('path 1.5-1.9 c38..48 (video 36..46)', [P[n] for n in range(36, 47)], 39.81)
