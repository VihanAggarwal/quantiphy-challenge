"""Credit card on the table plane: edge lengths vs 85.6 x 53.98 mm; plane scale implied; card range implied."""
import numpy as np
F, CX, CY = 711.0, 640.0, 360.0
pl = np.load('/home/user/quantiphy-challenge/research/next/labaudit/0040/plane.npy'); n, d0 = pl[:3], pl[3]
def ray(u, v):
    r = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return r / np.linalg.norm(r)
def on(u, v, s=1.0): r = ray(u, v); return s * d0 / (n @ r) * r
C = {'BL': (526, 529), 'BR': (617, 535), 'FR': (608, 551.5), 'FL': (510, 546)}
P = {k: on(*v) for k, v in C.items()}
L1 = np.linalg.norm(P['BR'] - P['BL']); L2 = np.linalg.norm(P['FR'] - P['FL'])
S1 = np.linalg.norm(P['FL'] - P['BL']); S2 = np.linalg.norm(P['FR'] - P['BR'])
print('long edges (s=1) cm', round(L1 * 100, 2), round(L2 * 100, 2), ' short edges', round(S1 * 100, 2), round(S2 * 100, 2))
s_long = 0.0856 / np.mean([L1, L2]); s_short = 0.05398 / np.mean([S1, S2])
cen = np.mean(list(P.values()), axis=0)
print('scale from long', round(s_long, 3), 'from short', round(s_short, 3))
print('card centre range s=1', round(np.linalg.norm(cen), 3), '-> with long-edge scale', round(np.linalg.norm(cen) * s_long, 3), 'stated 0.69')
