import numpy as np
rng = np.random.default_rng(1)
def unit(u, v, f):
    r = np.stack([(u - 640) / f, (v - 360) / f, np.ones_like(u)], -1)
    return r / np.linalg.norm(r, axis=-1, keepdims=True)
r0 = 70.45
clk = {'c37': (722.3, 368.8), 'c38': (754.6, 356.2), 'c39': (787.3, 359.1)}   # gravity-model pixels (mean of renders)
drm = {'A': -0.42, 'B': -0.56}
N = 400000
conv = np.where(rng.random(N) < 0.6, 'A', 'B')
f = np.where(rng.random(N) < 0.75, 711.0, 740.0)
a = np.where(conv == 'A', 'c38', 'c37'); b = np.where(conv == 'A', 'c39', 'c38')
u0 = np.array([clk[k][0] for k in a]) + rng.normal(0, 2.5, N); v0 = np.array([clk[k][1] for k in a]) + rng.normal(0, 2.5, N)
u1 = np.array([clk[k][0] for k in b]) + rng.normal(0, 2.5, N); v1 = np.array([clk[k][1] for k in b]) + rng.normal(0, 2.5, N)
mu = np.where(rng.random(N) < 0.6, 0.0, rng.normal(2.3, 1.5, N))
sig = rng.choice([1.0, 2.0, 3.0], N)
dr = np.array([drm[c] for c in conv]) + mu + rng.normal(0, 1, N) * sig
L = np.linalg.norm((r0 + dr)[:, None] * unit(u1, v1, f) - r0 * unit(u0, v0, f), axis=1) * 25
TH = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95])
def escore(x, L):
    rel = np.abs(x - L) / L
    return ((rel[:, None] < 1 - TH[None]).mean(1)).mean()
xs = np.arange(70, 121, 1.0)
sub = L[:100000]
es = [escore(x, sub) for x in xs]
i = int(np.argmax(es))
print('label mixture: mean %.1f median %.1f p10 %.1f p25 %.1f p75 %.1f p90 %.1f' % (L.mean(), np.median(L), *np.percentile(L, [10, 25, 75, 90])))
print('best x %.0f E[score] %.3f; E at 80 %.3f, 85 %.3f, 90 %.3f, 95 %.3f, 100 %.3f, 106.1 %.3f' % (xs[i], es[i], *[escore(x, sub) for x in [80, 85, 90, 95, 100, 106.076]]))
for c in ['A', 'B']:
    m = conv == c
    print(c, 'median %.1f mean %.1f' % (np.median(L[m]), L[m].mean()))
