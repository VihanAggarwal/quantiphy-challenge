# Clicked-point emulation (label procedure): ball click back-projected with the stated range, desk click with 1.725.
import numpy as np
cx=640.; cy=360.; R=0.116
n=np.load('/home/user/quantiphy-challenge/research/next/labaudit/0008/scripts/normal.npy')
def ray(p,f):
    r=np.array([p[0]-cx,p[1]-cy,f]); return r/np.linalg.norm(r)
for f in [700.,711.,722.]:
    print(f'--- f={f}')
    for h in [0.855]:
        print('  plane range at desk click (570,435): %.3f  (h=%.3f)'%(-h/(n@ray((570,435),f)),h))
    D=1.725*ray((570,435),f)
    for lab,(p,rg) in {'t=0 rest (R4 used)':((522,97),1.279),'t=0 rest @1.401':((522,97),1.401),
                       'frame 23 (t=0.958)':((523,131),1.401),'frame 24 (t=1.0)':((532,157),1.401),
                       'frame 24 (t=1.0) +R':((532,157),1.517),'apex 36 (t=1.5)':((548,305),1.5225),'apex R4 px':((549,301),1.5225)}.items():
        B=rg*ray(p,f); print(f'  {lab:22s} -> |B-D| = {100*np.linalg.norm(B-D):.1f} cm')
