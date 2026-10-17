import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0066.mp4')
c.set(cv2.CAP_PROP_POS_FRAMES, 40); ok, im = c.read()
g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(float)
def edges(p, off):
    d = np.diff(p)
    return off + np.argmax(np.abs(d))
# vertical maroon line near x~1720, blue line near x~1140, horizontal maroon line near y~160
for name, (xa, xb) in {'blue_v': (1080, 1220), 'maroon_v': (1650, 1800), 'maroon_v_left': (0, 120)}.items():
    for yr in [(300, 400), (600, 700), (850, 950)]:
        p = g[yr[0]:yr[1], xa:xb].mean(0)
        bg = np.median(p); ext = p.max() if name.startswith('blue') else p.min()
        thr = (bg + ext) / 2
        idx = np.nonzero(p > thr)[0] if name.startswith('blue') else np.nonzero(p < thr)[0]
        # subpixel
        i0, i1 = idx.min(), idx.max()
        l = i0 - 1 + (thr - p[i0 - 1]) / (p[i0] - p[i0 - 1]) if i0 > 0 else i0
        rr = i1 + (p[i1] - thr) / (p[i1] - p[i1 + 1]) if i1 < len(p) - 1 else i1
        print(name, yr, 'x=%.1f-%.1f width=%.1f' % (l + xa, rr + xa, rr - l))
for name, (xa, xb) in {'maroon_h': (300, 800), 'maroon_h2': (1200, 1500)}.items():
    p = g[100:260, xa:xb].mean(1)
    bg = np.median(p); ext = p.min(); thr = (bg + ext) / 2
    idx = np.nonzero(p < thr)[0]; i0, i1 = idx.min(), idx.max()
    l = i0 - 1 + (thr - p[i0 - 1]) / (p[i0] - p[i0 - 1]); rr = i1 + (p[i1] - thr) / (p[i1] - p[i1 + 1])
    print(name, 'y=%.1f-%.1f width=%.1f' % (l + 100, rr + 100, rr - l))
cr = im[100:260, 1600:1850]; cv2.imwrite('/home/user/quantiphy-challenge/research/next/audit3/internet_03/c66corner.png', cv2.resize(cr, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST))
