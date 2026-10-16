import numpy as np
from common import *
exec(open('wbplane.py').read().split('frames=[n')[0])
for f,(p,r) in {700:(39.34,8.43),711:(38.93,8.53),722:(38.50,8.66)}.items():
    nm=normal(p,r)
    for TL,BL,TR in [((843,518),(820,680),(1112,607)),((844,517),(820.5,680.5),(1111,606)),((842,519),(819,679),(1112.5,607.5))]:
        P=backproj(np.array([TL,BL,TR],float),nm,1.0,f)
        W=np.linalg.norm(P[1]-P[0]); L=np.linalg.norm(P[2]-P[0])
        a=(P[1]-P[0])@(P[2]-P[0])/W/L
        print(f,'static W/h=%.4f L/h=%.4f cos=%.3f  ratio %.3f'%(W,L,a,W/L))
