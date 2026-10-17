# Independent 2D tracker (round 2). Jar: near-white pixels; toy: yellow body (+ olive crown, reported separately).
# Uses x-render green-screen foreground where available; o/s use colour only. Reports centroid and bbox centre.
import sys; sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0020/scripts')
from common import *
R1 = json.load(open(ROOT + '/research/next/labaudit/0020/tracks.json'))

def fg_mask(im, r):
    b, g, rr = [im[..., k].astype(int) for k in range(3)]
    if r == 'x':
        return ~((g > 140) & (g - rr > 60) & (g - b > 60))
    if r == 's':
        # blue backdrop: b > r clearly, low brightness spread; keep everything not blue-grey backdrop
        return ~((b - rr > 25) & (b > 90) & (np.abs(g - (b + rr) / 2) < 40))
    return np.ones(im.shape[:2], bool)

def masks(im, r):
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(int)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    fg = fg_mask(im, r)
    jar = (s < 50) & (v > 185) & fg
    yel = (h >= 18) & (h <= 38) & (s > 70) & (v > 110) & fg
    crown = (h >= 25) & (h <= 50) & (s > 60) & (v > 50) & (v <= 140) & fg
    return jar, yel, crown

def comp_near(m, uv, win=60, minarea=30):
    u0, v0 = int(round(uv[0])), int(round(uv[1]))
    x0, y0 = max(0, u0 - win), max(0, v0 - win)
    sub = m[y0:v0 + win, x0:u0 + win].astype(np.uint8)
    sub = cv2.morphologyEx(sub, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(sub)
    best = None
    for k in range(1, n):
        if st[k, 4] < minarea: continue
        dd = np.hypot(cen[k][0] + x0 - uv[0], cen[k][1] + y0 - uv[1])
        sc = st[k, 4] - 3 * dd
        if best is None or sc > best[0]: best = (sc, k)
    if best is None: return None
    k = best[1]
    ys, xs = np.nonzero(lab == k)
    xs = xs + x0; ys = ys + y0
    return dict(c=[float(xs.mean()), float(ys.mean())],
                bb=[float((xs.min() + xs.max()) / 2), float((ys.min() + ys.max()) / 2)],
                wh=[int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)], area=int(len(xs)),
                pts=(xs, ys))

if __name__ == '__main__':
    out = {}
    for r in 'osx':
        fr = frames(r); out[r] = {'jar': {}, 'toy': {}, 'toyall': {}}
        for k in range(8, 30):
            jar, yel, crown = masks(fr[k], r)
            for obj, m in (('jar', jar), ('toy', yel), ('toyall', yel | crown)):
                ref = R1[r]['jar' if obj == 'jar' else 'toy'].get(str(k))
                if ref is None: continue
                res = comp_near(m, ref[:2])
                if res is None: continue
                res.pop('pts')
                out[r][obj][k] = res
        print('render', r)
        for k in range(10, 28):
            line = f'{k:2d} c{int(cap_index(k)):2d}'
            for obj in ('jar', 'toy', 'toyall'):
                q = out[r][obj].get(k)
                ref = R1[r]['jar' if obj == 'jar' else 'toy'].get(str(k))
                if q: line += f' | {obj} c({q["c"][0]:.1f},{q["c"][1]:.1f}) bb({q["bb"][0]:.1f},{q["bb"][1]:.1f}) wh{q["wh"]} a{q["area"]}'
                if obj != 'toyall' and ref: line += f' r1({ref[0]:.1f},{ref[1]:.1f})'
            print(line)
    json.dump(out, open(D + 'track2.json', 'w'))
