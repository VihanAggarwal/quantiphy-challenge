# Subpixel ball diameter from horizontal chords (partial-coverage at both ends) using a median background.
import cv2, numpy as np, sys, json
vid, trk = sys.argv[1], sys.argv[2]
tr = dict((i, r) for i, r in json.load(open(trk)))
c = cv2.VideoCapture(vid); frames = []
while True:
    ok, f = c.read()
    if not ok: break
    frames.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32))
n = len(frames)
bg = np.median(np.stack(frames[::3]), axis=0)
res = []
for i in range(n):
    r = tr.get(i)
    if r is None: continue
    cx, cy = r['cx'], r['cy']
    if cx < 30 or cx > frames[i].shape[1] - 30 or cy < 30 or cy > frames[i].shape[0] - 30: continue
    d = bg - frames[i]   # positive inside ball (ball darker than bg)
    best = []
    for row in range(int(cy) - 4, int(cy) + 5):
        prof = d[row, int(cx) - 25:int(cx) + 26]
        inner = np.median(prof[20:31])
        if inner < 15: continue
        frac = np.clip(prof / inner, 0, 1)
        # restrict to the connected run around centre
        m = frac > 0.5
        l = 25; rr = 25
        while l > 0 and m[l - 1]: l -= 1
        while rr < 50 and m[rr + 1]: rr += 1
        w = frac[l:rr + 1].sum() + (frac[l - 1] if l > 0 else 0) + (frac[rr + 1] if rr < 50 else 0)
        best.append(w)
    # vertical chords (top half only doubled is unreliable; take full but report)
    vb = []
    for col in range(int(cx) - 4, int(cx) + 5):
        prof = d[int(cy) - 25:int(cy) + 26, col]
        inner = np.median(prof[20:31])
        if inner < 15: continue
        frac = np.clip(prof / inner, 0, 1); m = frac > 0.5
        l = 25; rr = 25
        while l > 0 and m[l - 1]: l -= 1
        while rr < 50 and m[rr + 1]: rr += 1
        vb.append(frac[l:rr + 1].sum() + (frac[l - 1] if l > 0 else 0) + (frac[rr + 1] if rr < 50 else 0))
    if best:
        res.append((i, max(best), max(vb) if vb else np.nan))
for i, h, v in res: print(i, 'hchord %.2f vchord %.2f' % (h, v))
h = np.array([x[1] for x in res]); v = np.array([x[2] for x in res])
print('median hchord %.2f  median vchord %.2f' % (np.median(h), np.nanmedian(v)))
