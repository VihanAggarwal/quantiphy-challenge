"""Per-object tracking for captured_0018 renders (remeasure_b, independent).
Foreground = |frame - background| where background = median of frames 0..19 (objects held high,
floor/fall region empty).  For each object we follow a window from a seed, take the largest fg
blob (optionally colour-gated) and report centroid / bbox.  Results saved to tracks_<vid>.json.
"""
import cv2, numpy as np, json, sys

vid = sys.argv[1] if len(sys.argv) > 1 else 'captured_0018'
OUT = '/home/user/quantiphy-challenge/research/next/labaudit2/0018/remeasure_b'
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
fr = []
while True:
    ok, f = c.read()
    if not ok:
        break
    fr.append(f)
fr = np.array(fr)
bg0 = np.median(fr[0:20], axis=0).astype(np.int16)
bg1 = np.median(fr[44:49], axis=0).astype(np.int16)
hsv = [cv2.cvtColor(f, cv2.COLOR_BGR2HSV) for f in fr]

def fgmask(i, bg, thr=45):
    d = np.abs(fr[i].astype(np.int16) - bg).sum(2)
    return (d > thr).astype(np.uint8)

def colour_mask(i, hlo, hhi, smin):
    h = hsv[i]
    return ((h[..., 0] >= hlo) & (h[..., 0] <= hhi) & (h[..., 1] >= smin)).astype(np.uint8)

def track(name, seed, frames, win, gate=None, bgsel=None, minarea=20):
    res = {}
    px, py = seed
    vx = vy = 0.0
    for i in frames:
        bg = bg0 if (bgsel is None or bgsel(i) == 0) else bg1
        m = fgmask(i, bg)
        if gate is not None:
            m = m & gate(i)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        cx, cy = px + vx, py + vy
        x0, y0 = int(max(0, cx - win)), int(max(0, cy - win))
        x1, y1 = int(min(1280, cx + win)), int(min(720, cy + win))
        sub = m[y0:y1, x0:x1]
        n, lab, st, cen = cv2.connectedComponentsWithStats(sub)
        best = None
        for k in range(1, n):
            a = st[k, 4]
            if a < minarea:
                continue
            dist = np.hypot(cen[k][0] + x0 - cx, cen[k][1] + y0 - cy)
            score = a / (1 + dist / 10.0)
            if best is None or score > best[0]:
                best = (score, k)
        if best is None:
            res[i] = None
            continue
        k = best[1]
        ys, xs = np.nonzero(lab == k)
        ux, uy = xs.mean() + x0, ys.mean() + y0
        bb = [int(xs.min() + x0), int(ys.min() + y0), int(xs.max() + x0), int(ys.max() + y0)]
        res[i] = dict(c=[float(ux), float(uy)], bb=bb, a=int(len(xs)))
        vx, vy = ux - px, uy - py
        px, py = ux, uy
    return res

if __name__ == '__main__':
    tr = {}
    # tennis ball: yellow-green
    tr['tennis'] = track('tennis', (761, 249), range(20, 49), 45,
                         gate=lambda i: colour_mask(i, 25, 50, 60))
    tr['pineapple'] = track('pineapple', (870, 257), range(20, 49), 60,
                            gate=lambda i: colour_mask(i, 12, 32, 90), minarea=40)
    json.dump(tr, open(f'{OUT}/tracks_{vid}.json', 'w'))
    for k, v in tr.items():
        print(k)
        for i, r in v.items():
            print(' ', i, None if r is None else ([round(x, 1) for x in r['c']], r['bb'], r['a']))
