import numpy as np
from common import *
exec(open('wbplane.py').read().split('frames=[n')[0])
def proj(X,f): return np.array([CX+f*X[0]/X[2], CY+f*X[1]/X[2]])
for f,(p,r) in {700:(39.34,8.43),711:(38.93,8.53),722:(38.50,8.66)}.items():
    nrm=normal(p,r)
    for (ub,vb,vt) in [(335,209.5,136),(335,209.5,135),(320,208.5,136),(345,208.5,135)]:
        B=backproj(np.array([[ub,vb]]),nrm,1.0,f)[0]
        # find H
        Hs=np.linspace(0,0.5,50001)
        vs=np.array([proj(B-H*nrm,f)[1] for H in Hs[::50]])
        H=np.interp(-vt,-vs,Hs[::50])
        rng=np.linalg.norm(B)
        print(f,(ub,vb,vt),'H/h=%.4f  h(for 37.5cm)=%.3f  bottom range/h=%.3f -> range at h=1.88: %.2f'%(H,0.375/H,rng,rng*1.88))
