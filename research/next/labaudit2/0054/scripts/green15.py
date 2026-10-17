from common import *
from tracks import *
from fit_a import fit, model, gd, proj
R=0.0335
for pitch in [0,1]:
    g=gd(pitch)
    p,rms=fit(A_G_raw,list(range(24,37)),g)
    C38=model(p,np.array([1.52]),1.0,g)[0]; C37=model(p,np.array([1.48]),1.0,g)[0]
    Vh=p[3:6]-(p[3:6]@g)*g  # horizontal velocity
    o39=A_G_raw[37]; d39=ray(*o39)
    # route A: plane down = H - R - eps
    for H in [0.86,0.90,0.93]:
        for eps in [0.0,0.03]:
            s=(H-R-eps)/(d39@g); P39=s*d39
            print(f'pitch {pitch} H={H} eps={eps}: r39={s:.3f} v38-39={np.linalg.norm(P39-C38)*25:.2f}  (C38 down={C38@g:.3f})')
    # route B: horizontal continuity: P39 horizontal position = C38_h + Vh*0.04 (approx), find point on ray closest
    Ch=C38+Vh*0.04
    s=(Ch@d39); P39=s*d39  # closest point on ray to Ch
    print(f'pitch {pitch} horiz-continuity: r39={s:.3f} down39={P39@g:.3f} v38-39={np.linalg.norm(P39-C38)*25:.2f}; v37-38={np.linalg.norm(C38-C37)*25:.2f}')
