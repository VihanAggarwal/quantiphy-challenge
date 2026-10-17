"""Look for the dropped capture frames: (1) dense optical flow magnitude of the person (torso/legs, arm) per video step;
(2) toy track steps during the roll."""
import cv2, numpy as np
from common import *
fr = load('o')
g = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in fr]
regs = {'torso': (120, 330, 420, 560), 'legs': (330, 720, 380, 560), 'head': (20, 140, 400, 560), 'raised arm': (150, 330, 560, 700), 'left arm': (120, 380, 300, 420)}
rows = []
for i in range(len(g) - 1):
    fl = cv2.calcOpticalFlowFarneback(g[i], g[i + 1], None, 0.5, 3, 21, 3, 5, 1.2, 0)
    r = []
    for k, (y0, y1, x0, x1) in regs.items():
        f = fl[y0:y1, x0:x1].reshape(-1, 2)
        r.append(np.median(f[:, 0])); r.append(np.median(f[:, 1])); r.append(np.mean(np.linalg.norm(f, axis=1)))
    rows.append(r)
    print('%2d->%2d ' % (i, i + 1) + ' | '.join('%s %+.2f %+.2f m%.2f' % (k[:5], r[3 * j], r[3 * j + 1], r[3 * j + 2]) for j, k in enumerate(regs)))
