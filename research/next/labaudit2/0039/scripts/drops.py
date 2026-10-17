"""Look for dropped capture frames: frame-to-frame motion energy in regions with continuous motion
(person under / behind the table in the o render), and dense optical-flow magnitude there."""
import cv2, numpy as np, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0039/scripts')
from frames import load
fr = load('0039')
g = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in fr]
regs = {'under_table': (590, 720, 430, 800), 'behind_left': (380, 460, 500, 640)}
for name, (y0, y1, x0, x1) in regs.items():
    out = []
    for k in range(len(g) - 1):
        a = g[k][y0:y1, x0:x1]; b = g[k + 1][y0:y1, x0:x1]
        fl = cv2.calcOpticalFlowFarneback(a, b, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag = np.linalg.norm(fl, axis=-1)
        out.append((k, np.abs(a.astype(int) - b).mean(), np.median(fl[..., 0]), np.median(fl[..., 1]), np.percentile(mag, 90)))
    print('==', name)
    print('\n'.join(f'{k:2d}->{k+1:2d} absdiff {d:5.2f} flow med ({fx:5.2f},{fy:5.2f}) p90 {m:5.2f}' for k, d, fx, fy, m in out))
