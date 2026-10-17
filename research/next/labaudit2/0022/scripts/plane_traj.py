"""Plane-model 3D ball-centre trajectory per video frame (o/x/s, f 711 and 716), steps per capture interval,
smooth speed by local polynomial fits on the 25 fps capture clock."""
import sys, json, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0022/scripts')
from common import *
T = json.load(open(f'{B}/track.json')); P = json.load(open(f'{B}/plane.json'))
K = np.arange(12, 47)
def traj(tag, key='711.0_far=76'):
    n = np.array(P[key]['n']); d = P[key]['d']; f = float(key.split('_')[0])
    out = []
    for k in range(49):
        r = ray(*T[tag][k][:2], f=f); out.append((d - 0.02) / (n @ r) * r)
    return np.array(out)
if __name__ == '__main__':
    for key in ['711.0_far=76', '716.0_far=76']:
        for tag in ['o', 'x', 's']:
            C = traj(tag, key); c = cap_of_video(np.arange(49))
            step = np.linalg.norm(np.diff(C, axis=0), axis=1) / np.diff(c) * 100  # cm per capture frame
            rad = -np.diff(np.linalg.norm(C, axis=1)) / np.diff(c) * 100
            print(key, tag, 'cm/capture-frame steps v11..46:', ' '.join(f'{x:.2f}' for x in step[11:46]))
            if tag == 'o':
                print('   radial approach per capture frame:', ' '.join(f'{x:.2f}' for x in rad[11:46]))
            # smooth speed: quadratic fit of each coordinate vs capture time over a window of +-5 video frames
            for kk, lab in [(19, 'c20 (t .8)'), (29, 'c30 (t1.2)')]:
                for hw in (3, 5, 7):
                    idx = np.arange(kk - hw, kk + hw + 2)  # include next frame (forward-difference midpoint)
                    t = c[idx] / 25.0; tm = (c[kk] + 0.5) / 25.0
                    co = [np.polyfit(t - tm, C[idx, j], 2) for j in range(3)]
                    v = np.array([cc[1] for cc in co]); a = np.array([2 * cc[0] for cc in co])
                    v0 = np.array([np.polyval(np.polyder(cc), (c[kk] / 25.0) - tm) for cc in co])
                    print(f'   {lab} hw {hw}: smooth |v| at mid-step {np.linalg.norm(v) * 100:.1f}, at t {np.linalg.norm(v0) * 100:.1f} cm/s, '
                          f'a along v {a @ v / np.linalg.norm(v) * 100:.1f} cm/s2, sin_psi {np.linalg.norm(np.cross(v / np.linalg.norm(v), C[kk] / np.linalg.norm(C[kk]))):.2f}')
