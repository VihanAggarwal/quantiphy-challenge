"""Ball blob per frame: centroid, principal axes (minor axis ~ ball diameter under linear motion blur)."""
import cv2, numpy as np, sys, json
R = sys.argv[1] if len(sys.argv) > 1 else 'x'
base = '/home/user/quantiphy-challenge/research/next/labaudit/0040/frames'
fr = [cv2.imread(f'{base}/v{R}_{i:02d}.png') for i in range(49)]
A = np.stack(fr).astype(np.int16)
med = np.median(A, axis=0)
out = {}
for i in range(49):
    d = np.abs(A[i] - med).max(-1)
    g = cv2.cvtColor(fr[i], cv2.COLOR_BGR2GRAY)
    m = ((d > 35) & (g > 120)).astype(np.uint8)
    m[690:] = 0
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n <= 1: continue
    k = 1 + np.argmax(st[1:, 4])
    ys, xs = np.nonzero(lab == k)
    c = np.array([xs.mean(), ys.mean()])
    C = np.cov(np.vstack([xs, ys]))
    w, v = np.linalg.eigh(C)
    minor, major = 4 * np.sqrt(w[0]), 4 * np.sqrt(w[1])
    ang = np.degrees(np.arctan2(v[1, 1], v[0, 1]))
    out[i] = dict(u=c[0], v=c[1], minor=minor, major=major, ang=ang, area=int(st[k, 4]))
    print(f'{i:2d} t={i/24:.3f} c=({c[0]:7.1f},{c[1]:6.1f}) minor={minor:5.1f} major={major:5.1f} ang={ang:6.1f} area={st[k,4]}')
json.dump(out, open(f'/home/user/quantiphy-challenge/research/next/labaudit/0040/track_{R}.json', 'w'), indent=1)
