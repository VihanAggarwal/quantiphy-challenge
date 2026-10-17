# Compare speed/accel profiles of the 0253 box (own prior 0.611 m / 85 px) and 0254 ball (own prior 0.17 m / D px).
import json, numpy as np, sys
S = sys.argv[1]
tb = json.load(open(S + '/t0253.json'))
ang = np.deg2rad(44.25); u = np.array([np.cos(ang), np.sin(ang)])
# box: centroid along slope (frames 13-44, skip 27 which shows true frame 28 -> remap 27->28 handled by dropping)
box = {i: (tb[i]['cx'], tb[i]['cy']) for i in range(13, 45) if i != 27}
# box leading edge (smax, computed with 42.8 deg axis; fine for 1-D steps), frames 5-16 with true-frame remap 9->10, 10->11, drop 11
lead = {}
for vf, trf in [(5, 5), (6, 6), (7, 7), (8, 8), (9, 10), (10, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18)]:
    lead[trf] = tb[vf]['smax']
ball = {}
for l in open(S + '/c0254_radial.txt'):
    i, x, y = l.split(); i = int(i)
    if 20 <= i <= 47: ball[i] = (float(x), float(y))
def prof(d, scale, deg=3, q=(12, 24, 36, 42)):
    fr = sorted(d); F = np.array(fr, float)
    if isinstance(d[fr[0]], tuple):
        P = np.array([d[i] for i in fr]); s = P @ u
    else:
        s = np.array([d[i] for i in fr])
    c = np.polyfit(F, s, deg); rms = np.sqrt(np.mean((np.polyval(c, F) - s) ** 2))
    out = []
    for f in q:
        v1 = (np.polyval(c, f) - np.polyval(c, f - 1)) * 24 * scale; v0 = (np.polyval(c, f - 1) - np.polyval(c, f - 2)) * 24 * scale
        out.append((f, v1, (v1 - v0) * 24))
    # time where v=0 (backward diff)
    vv = [(np.polyval(c, f) - np.polyval(c, f - 1)) for f in np.arange(-10, 20, 0.05)]
    return rms, out
for name, d, sc in (('box centroid 0.611/85', box, 0.611 / 85), ('ball circle D=25', ball, 0.17 / 25), ('ball circle D=24.4', ball, 0.17 / 24.4)):
    for deg in (2, 3):
        rms, out = prof(d, sc, deg)
        print('%-22s deg%d rms %.2f px | ' % (name, deg, rms) + ' | '.join('t=%.2f v=%.2f a=%.2f' % (f / 24, v, a) for f, v, a in out))
# box leading edge, local quadratic over true frames 5-18 -> speed and accel at f12
fr = sorted(lead); F = np.array(fr, float); s = np.array([lead[i] for i in fr])
for deg in (2, 3):
    c = np.polyfit(F, s, deg); rms = np.sqrt(np.mean((np.polyval(c, F) - s) ** 2))
    sc = 0.611 / 85
    v12 = (np.polyval(c, 12) - np.polyval(c, 11)) * 24 * sc; v11 = (np.polyval(c, 11) - np.polyval(c, 10)) * 24 * sc
    vs = [(np.polyval(c, f) - np.polyval(c, f - 1)) for f in np.arange(0, 12, 0.1)]
    f0 = np.arange(0, 12, 0.1)[np.argmin(np.abs(vs))]
    print('box leading edge true f5-18 deg%d rms %.2f: v(0.5)=%.2f a(0.5)=%.2f ; backward-diff speed ~0 at frame %.1f' % (deg, rms, v12, (v12 - v11) * 24, f0))
print('leading-edge per-frame steps (true frames):', ' '.join('%d:%.1f' % (fr[k + 1], s[k + 1] - s[k]) for k in range(len(fr) - 1) if fr[k + 1] - fr[k] == 1))
# ball cubic extrapolation: when is speed zero?
fr = sorted(ball); F = np.array(fr, float); P = np.array([ball[i] for i in fr]); s = P @ u
c = np.polyfit(F, s, 3); vs = np.polyval(np.polyder(c), np.arange(-10, 20, 0.1)); print('ball cubic: dp/df=0 at frame %.1f' % np.arange(-10, 20, 0.1)[np.argmin(np.abs(vs))])
