"""Physical acceleration around 1.2 s: plane-model speed per capture step vs time, linear fits over several
windows (video 16-44 and +-6/+-8 frames around video 29), scaled plane (x1.013), all renders, both clock mappings."""
import sys, json, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0022/scripts')
from common import *
from plane_traj import traj
for drop12 in (True, False):
    for tag in 'osx':
        C = traj(tag) * 1.013; cc = cap_of_video(np.arange(49), drop12)
        sp = np.linalg.norm(np.diff(C, axis=0), axis=1) / np.diff(cc) * 25 * 100   # cm/s per step
        tm = (cc[:-1] + cc[1:]) / 2 / 25
        out = []
        for lo, hi in [(16, 44), (21, 37), (23, 35), (16, 35)]:
            i = np.arange(lo, hi); a, b = np.polyfit(tm[i], sp[i], 1)
            out.append(f'v{lo}-{hi}: a {a:5.1f} cm/s2, v(1.2) {a * 1.2 + b:4.1f}')
        print(f'drop12={drop12} {tag}: ' + '; '.join(out))
