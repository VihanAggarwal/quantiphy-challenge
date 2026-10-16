"""Track the white ball in each render by difference from the per-pixel median frame."""
import cv2, numpy as np, sys
R = sys.argv[1] if len(sys.argv) > 1 else 'x'
base = '/home/user/quantiphy-challenge/research/next/labaudit/0040/frames'
fr = [cv2.imread(f'{base}/v{R}_{i:02d}.png') for i in range(49)]
A = np.stack(fr).astype(np.int16)
med = np.median(A, axis=0)
for i in range(49):
    d = np.abs(A[i] - med).sum(-1)
    g = cv2.cvtColor(fr[i], cv2.COLOR_BGR2GRAY)
    m = ((d > 60) & (g > 150)).astype(np.uint8)
    m[690:] = 0  # watermark
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n <= 1:
        print(i, 'none'); continue
    k = 1 + np.argmax(st[1:, 4])
    x, y, w, h, a = st[k]
    print(f'{i:2d} t={i/24:.3f} c=({cen[k][0]:.1f},{cen[k][1]:.1f}) bbox w={w} h={h} area={a} eqd={2*np.sqrt(a/np.pi):.1f}')
