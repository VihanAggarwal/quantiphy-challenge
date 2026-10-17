"""Soccer ball diameter from camera a: silhouette 144 x 142 px centred (793.5, 418) in ax frame 45, stated surface range 0.894."""
import sys, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0034/scripts')
from geom import ray, extents
def bisect(g, a, b):
    for _ in range(60):
        m = (a + b) / 2
        if g(a) * g(m) <= 0: b = m
        else: a = m
    return (a + b) / 2
u, v, W, H = 793.5, 418, 144, 142
for f in (692, 711, 745, 781):
    R = bisect(lambda R: extents(ray(u, v, f) * (0.894 + R), R, f)[0] - W, 0.03, 0.2)
    R2 = bisect(lambda R: extents(ray(u, v, f) * (0.894 + R), R, f)[1] - H, 0.03, 0.2)
    th = np.arccos(np.clip(ray(721.5, 418, f) @ ray(865.5, 418, f), -1, 1))
    chord = 2 * 0.894 * np.sin(th / 2)
    dl = np.sqrt((0.894 + R) ** 2 - R ** 2); chord2 = 2 * dl * np.sin(th / 2)
    print(f'f={f}: D(width) {2*R*100:.1f}  D(height) {2*R2*100:.1f} | label chord, both clicks at 0.894: {chord*100:.1f}; at limb range: {chord2*100:.1f}')
