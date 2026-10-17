import numpy as np
rng = np.random.default_rng(0)
def unit(u, v, f):
    r = np.stack([(u - 640) / f, (v - 360) / f, np.ones_like(u)], -1)
    return r / np.linalg.norm(r, axis=-1, keepdims=True)
r0 = 70.45
# click pixels (mean of 3 renders); c37 from the arc model projection
clk = {'c37': (722.3, 368.8), 'c38': (753.4, 356.8), 'c39': (785.7, 358.0)}
dr_model = {'A': -0.42, 'B': -0.56}
for conv, (a, b) in {'A': ('c38', 'c39'), 'B': ('c37', 'c38')}.items():
    for f in [711, 740]:
        for sig_tof in [0.0, 1.0, 2.0, 3.0]:
            N = 200000
            u0 = clk[a][0] + rng.normal(0, 2.5, N); v0 = clk[a][1] + rng.normal(0, 2.5, N)
            u1 = clk[b][0] + rng.normal(0, 2.5, N); v1 = clk[b][1] + rng.normal(0, 2.5, N)
            dr = dr_model[conv] + rng.normal(0, sig_tof, N)
            P0 = r0 * unit(u0, v0, f); P1 = (r0 + dr)[:, None] * unit(u1, v1, f)
            sp = np.linalg.norm(P1 - P0, axis=1) * 25
            print('%s f%d sigma_dr %.1f cm: mean %.1f median %.1f  IQR %.1f-%.1f' % (conv, f, sig_tof, sp.mean(), np.median(sp), *np.percentile(sp, [25, 75])))
