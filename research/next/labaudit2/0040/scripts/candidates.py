"""Expected MRA of candidate answers for v(1.5) and v(1.4) under label-noise scenarios.
Geometry: track points at capture 38/39 (v1.5) and 35/36 (v1.4) with anchor ranges ('track'), and the same
displacement rescaled to the ballistic FD magnitude ('ballistic'). Own-measurement scatter sig_A = 0.06."""
import sys, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0040/scripts')
sys.path.insert(0, '/home/user/quantiphy-challenge/research/labnoise')
import motion as M, labmodel as LM
def mra(pred, gt):
    rel = np.abs(pred - gt) / gt; return (rel[..., None] < 1 - LM.THR).mean(-1)
tr = M.load('x', 'caps')
P = {n: M.rng_anchor(M.cap(n)) * M.ray(tr[n]['u'], tr[n]['v']) for n in tr}
rng = np.random.default_rng(7)
def table(name, a, b, targets, cands, n=20000):
    d = b - a; base = np.linalg.norm(d) * 2500
    print(f'== {name}  (track FD {base:.1f})')
    print('   scenario              ' + ' '.join(f'{c:7.1f}' for c in cands))
    for tgt in targets:
        for sz in (0.0, 0.01, 0.02, 0.03):
            k = tgt / base * np.exp(rng.normal(0, 0.06, n))
            pts = np.stack([np.broadcast_to(a, (n, 3)), a + k[:, None] * d], axis=1)
            L = LM.path_labels_s(pts, 2.0, sz, seed=11) * 2500
            print(f'   phys {tgt:5.1f} sz={sz:.2f}       ' + ' '.join(f'{mra(c, L).mean():7.3f}' for c in cands))
table('v(1.5) c38->39', P[36], P[37], (77.1, 82.5), [72, 77, 80, 82, 85, 88, 92, 106.076])
table('v(1.4) c35->36', P[34], P[35], (125.4, 132.0, 141.0), [106.076, 115, 120, 125, 130, 135, 140])
