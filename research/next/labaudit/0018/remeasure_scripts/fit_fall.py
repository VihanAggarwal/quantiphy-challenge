import numpy as np

# centroids from track_fall.py output (frame: cy); bbox top/bottom for box
ball = {30:269.2,31:274.2,32:287.2,33:304.6,34:326.3,35:352.8,36:416.9,38:496.6}
box_c = {32:308.7,33:326.0,34:351.0,35:380.9,36:455.0,37:489.1,38:530.0}
box_top = {32:283,33:292,34:317,35:348,36:413,37:453,38:496}
box_bot = {32:283+55,33:292+70,34:317+70,35:348+68,36:413+80,37:453+73,38:496+74}
def tt(f, gap):
    return f - 31 + (gap if f >= 36 else 0)
def fitone(d, frames, gap=None):
    fs = [f for f in frames if f in d]
    if gap is None:
        fs = [f for f in fs if f <= 35]
        t = np.array([f-31 for f in fs], float); y = np.array([d[f] for f in fs])
        A = np.vstack([np.ones_like(t), t, t**2]).T
        c, res, *_ = np.linalg.lstsq(A, y, rcond=None)
        return 2*c[2], y - A@c
    t = np.array([tt(f, gap) for f in fs]); y = np.array([d[f] for f in fs])
    A = np.vstack([np.ones_like(t), t, t**2]).T
    c, *_ = np.linalg.lstsq(A, y, rcond=None)
    return 2*c[2], y - A@c
print('no-gap fits, frames<=35')
for name, d, fr in [('ball31-35', ball, range(31,36)), ('ball32-35', ball, range(32,36)), ('box_c32-35', box_c, range(32,36)), ('box_top32-35', box_top, range(32,36)), ('box_bot32-35', box_bot, range(32,36))]:
    a, r = fitone(d, fr)
    print(name, 'a_px/frame2=%.2f' % a, 'res', np.round(r, 1))
# joint fit with common gap
def resid(p):
    gap, *rest = p
    r = []
    for k, (d, fr) in enumerate([(ball, range(31,39)), (box_c, range(32,39))]):
        y0, v, a = rest[3*k:3*k+3]
        for f in fr:
            if f in d:
                t = tt(f, gap); r.append(d[f] - (y0 + v*t + 0.5*a*t*t))
    return r
best=None
for gap in np.arange(0,4.01,0.05):
    ab, rb = fitone(ball, range(31,39), gap); ax, rx = fitone(box_c, range(32,39), gap)
    s=np.sum(rb**2)+np.sum(rx**2)
    if best is None or s<best[0]: best=(s,gap,ab,ax)
print('joint best gap %.2f ball a %.2f box a %.2f' % best[1:], 'ratio %.3f'%(best[3]/best[2]))
for gap in [1.0, 1.5, 2.0, 2.5]:
    ab, rb = fitone(ball, range(31,39), gap); ax, rx = fitone(box_c, range(32,39), gap)
    print('gap', gap, 'ball a %.2f rms %.1f | box a %.2f rms %.1f | ratio %.3f' % (ab, np.sqrt(np.mean(rb**2)), ax, np.sqrt(np.mean(rx**2)), ax/ab))
