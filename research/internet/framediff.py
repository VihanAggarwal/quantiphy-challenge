"""Per-clip consecutive-frame differences: duplicate frames (diff ~ 0) and their spacing."""
import sys, glob, os, cv2, numpy as np
for f in sorted(glob.glob('data/QuantiPhy/internet_*.mp4')):
    cap = cv2.VideoCapture(f); prev = None; ds = []
    while True:
        ok, im = cap.read()
        if not ok: break
        g = cv2.resize(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), (320, 180)).astype(np.float32)
        if prev is not None: ds.append(float(np.mean(np.abs(g - prev))))
        prev = g
    ds = np.array(ds); med = np.median(ds)
    dup = np.where(ds < 0.15 * med)[0] + 1 if med > 0 else []
    print(os.path.basename(f)[:-4], len(ds) + 1, 'med %.2f' % med, 'dups', len(dup), list(dup[:12]))
