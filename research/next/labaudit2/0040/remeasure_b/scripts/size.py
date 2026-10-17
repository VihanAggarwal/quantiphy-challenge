import cv2, numpy as np, json, sys
B = '/home/user/quantiphy-challenge/research/next/labaudit2/0040/remeasure_b/'
V = sys.argv[1] if len(sys.argv) > 1 else 'captured_0040'
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4' % V)
fr = []
while True:
    ok, f = c.read()
    if not ok: break
    fr.append(f)
fr = np.array(fr).astype(np.float32)
bg = np.median(fr[28:49], axis=0)
T = json.load(open(B + 'track_%s.json' % V))
def bilin(img, x, y):
    return cv2.remap(img, x.astype(np.float32), y.astype(np.float32), cv2.INTER_LINEAR)
out = {}
for k in range(30, 49):
    t = T[str(k)]
    d = np.abs(fr[k] - bg).max(axis=2)
    d = cv2.GaussianBlur(d, (3, 3), 0)
    cx, cy = t['cx'], t['cy']
    a = np.radians(t['ang'])
    mdir = np.array([np.cos(a), np.sin(a)]); pdir = np.array([-mdir[1], mdir[0]])
    s = np.arange(-50, 50.01, 0.25)
    widths = []; peaks = []
    for off in np.arange(-4, 4.01, 1.0):
        x = cx + off * mdir[0] + s * pdir[0]; y = cy + off * mdir[1] + s * pdir[1]
        prof = bilin(d, x[None], y[None]).ravel()
        pk = np.percentile(prof, 97)
        half = pk / 2
        above = np.nonzero(prof > half)[0]
        if len(above) == 0: continue
        i0, i1 = above[0], above[-1]
        # subpixel crossings
        def cross(i, j):
            return s[i] + (half - prof[i]) / (prof[j] - prof[i]) * (s[j] - s[i])
        lo = cross(i0 - 1, i0); hi = cross(i1, i1 + 1)
        widths.append(hi - lo); peaks.append(pk)
    # also along-motion length
    x = cx + s * mdir[0]; y = cy + s * mdir[1]
    prof = bilin(d, x[None], y[None]).ravel(); pk = np.percentile(prof, 97); above = np.nonzero(prof > pk / 2)[0]
    L = s[above[-1]] - s[above[0]]
    out[k] = dict(D=float(np.median(widths)), Dsd=float(np.std(widths)), L=float(L), peak=float(np.median(peaks)))
    print(k, 'perp FWHM %.1f (sd %.1f)  along %.1f  peak %.0f' % (out[k]['D'], out[k]['Dsd'], L, out[k]['peak']))
json.dump(out, open(B + 'size_%s.json' % V, 'w'), indent=1)
