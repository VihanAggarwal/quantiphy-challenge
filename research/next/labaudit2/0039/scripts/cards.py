"""Flat playing card in front of the tower: plane side lengths (tells the card size, hence the possible tent height)."""
import numpy as np, json
OUT = '/home/user/quantiphy-challenge/research/next/labaudit2/0039'
F, CX, CY = 711.0, 640.0, 360.0
pl = json.load(open(f'{OUT}/plane.json')); n = np.array(pl['n_vp']); H0 = pl['h_vp']
def ray(p): return np.array([(p[0] - CX) / F, (p[1] - CY) / F, 1.0])
TL, TR, BR, BL = (644, 502.5), (738, 506.5), (747, 515), (657, 516)
for hf in (0.98, 1.0, 1.02):
    H = H0 * hf
    Q = [H / (n @ ray(p)) * ray(p) for p in (TL, TR, BR, BL)]
    s = [np.linalg.norm(Q[i] - Q[(i + 1) % 4]) * 100 for i in range(4)]
    print(f'h x{hf}: flat card sides top {s[0]:.2f} right {s[1]:.2f} bottom {s[2]:.2f} left {s[3]:.2f}; centre range {np.linalg.norm(np.mean(Q,0)):.4f}')
