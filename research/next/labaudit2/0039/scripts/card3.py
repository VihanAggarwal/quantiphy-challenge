"""Credit card: hand-read corners (from intensity rows/cols of the x-render median) -> table plane -> side lengths."""
import numpy as np, json
OUT = '/home/user/quantiphy-challenge/research/next/labaudit2/0039'
F, CX, CY = 711.0, 640.0, 360.0
pl = json.load(open(f'{OUT}/plane.json')); n = np.array(pl['n_vp']); H0 = pl['h_vp']
def ray(p): return np.array([(p[0] - CX) / F, (p[1] - CY) / F, 1.0])
TL, BL, TR, BR = (525.5, 532.5), (519.0, 548.5), (619.5, 533.5), (620.0, 550.5)
for hf in (0.98, 1.0, 1.02):
    H = H0 * hf
    Q = [H / (n @ ray(p)) * ray(p) for p in (TL, TR, BR, BL)]
    s = [np.linalg.norm(Q[i] - Q[(i + 1) % 4]) * 100 for i in range(4)]
    d = [np.linalg.norm(Q[0] - Q[2]) * 100, np.linalg.norm(Q[1] - Q[3]) * 100]
    c = np.mean(Q, 0)
    print(f'h x{hf}: sides top {s[0]:.2f} right {s[1]:.2f} bottom {s[2]:.2f} left {s[3]:.2f}; diagonals {d[0]:.2f} {d[1]:.2f}; area {s[0]*s[1]:.1f}; centre range {np.linalg.norm(c):.4f}')
print('ID-1 card: 8.56 x 5.40, diagonal 10.12')
# stated-range route: horizontal extent and 3D at range 0.6867
Q = [0.6867 * ray(p) / np.linalg.norm(ray(p)) for p in (TL, TR, BR, BL)]
print('stated range 0.6867 for all corners: top', np.linalg.norm(Q[0] - Q[1]) * 100, 'bottom', np.linalg.norm(Q[3] - Q[2]) * 100)
