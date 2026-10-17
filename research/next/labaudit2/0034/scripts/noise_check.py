"""Expected noisy labels for the S-route camera-a track under the pipeline's own label-noise emulator
(research/labnoise/labmodel.py: click jitter sigma_px, ToF range noise sigma_z, f 722), per capture frame.
Paths over the moving capture frames (speed >= 25% of max, as in labnoise/emulate.py) and over all frames."""
import sys, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0034/scripts')
sys.path.insert(0, '/home/user/quantiphy-challenge/research/labnoise')
import labmodel as LM
from labelstyle import track, cap, N
for f in (711,):
    for b in 'LR':
        C, S = track(b, f, 'S')
        cv = np.array([cap(k) for k in range(N)])
        cc = np.arange(cv[0], cv[-1] + 1)
        Sc = np.stack([np.interp(cc, cv, S[:, j]) for j in range(3)], 1)      # per capture frame (dropped ones interpolated)
        spd = np.r_[np.linalg.norm(np.diff(Sc, axis=0), axis=1), 0] * 25
        mv = np.where(spd >= max(0.25 * spd.max(), 0.05))[0]
        Qm = Sc[mv[0]:mv[-1] + 2]
        det_m = np.linalg.norm(np.diff(Qm, axis=0), axis=1).sum(); det_a = np.linalg.norm(np.diff(Sc, axis=0), axis=1).sum()
        print(f'{b}: moving capture frames {cc[mv[0]]}..{cc[mv[-1]+1]}  deterministic path moving {det_m*100:.1f}  all {det_a*100:.1f}')
        p30 = Sc[30]; v30 = (Sc[31] - Sc[30]) * 25
        for sz in (0.0, 0.005, 0.01, 0.02, 0.03):
            Lm = LM.path_labels(Qm, 2.0, sz, n=3000) * 100; La = LM.path_labels(Sc, 2.0, sz, n=3000) * 100
            V = LM.speed_labels(p30, v30, 2.0, sz, n=6000) * 100
            print(f'   sigma_z {sz*100:.1f} cm: path(moving) mean {Lm.mean():5.1f} median {np.median(Lm):5.1f} | path(all) mean {La.mean():6.1f} '
                  f'| v1.2 deterministic {np.linalg.norm(v30)*100:5.1f} noisy mean {V.mean():5.1f} median {np.median(V):5.1f}')
