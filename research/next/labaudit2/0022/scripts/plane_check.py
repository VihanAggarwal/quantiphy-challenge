"""Ball centre on the plane 2 cm above the table top (PnP plane), surface range = centre range - 0.02,
compared with the stated ranges at t = 0.6/0.8/1.2 (capture 15/20/30 = video 14/19/29)."""
import sys, json, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0022/scripts')
from common import *
T = json.load(open(f'{B}/track.json')); P = json.load(open(f'{B}/plane.json'))
stated = {14: 1.751, 19: 1.687, 29: 1.526}
for key in ['711.0_far=76', '716.0_far=76']:
    n = np.array(P[key]['n']); d = P[key]['d']; f = float(key.split('_')[0])
    for tag in ['o', 'x', 's']:
        tr = T[tag]
        s = []
        for k, R in stated.items():
            r = ray(*tr[k][:2], f=f); C = (d - 0.02) / (n @ r) * r
            s.append(f'v{k}: plane surf {np.linalg.norm(C) - 0.02:.4f} vs stated {R} ({(np.linalg.norm(C) - 0.02 - R) * 100:+.1f} cm)')
        print(key, tag, '; '.join(s))
