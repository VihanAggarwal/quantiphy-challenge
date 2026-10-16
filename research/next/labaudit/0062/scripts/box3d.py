import numpy as np
from common import *
exec(open('wbplane.py').read().split('frames=[n')[0])
def proj(X,f): return np.array([CX+f*X[0]/X[2], CY+f*X[1]/X[2]])
def Hfit(B_uv,T_uv,nrm,f):
    B=backproj(np.array([B_uv]),nrm,1.0,f)[0]
    Hs=np.linspace(0,0.2,4001); vs=np.array([proj(B-H*nrm,f)[1] for H in Hs])
    return np.interp(-T_uv[1],-vs,Hs)
for f,(p,r) in {700:(39.34,8.43),711:(38.93,8.53),722:(38.50,8.66)}.items():
    nrm=normal(p,r)
    for (Bnl,Tnl,top) in [((493,522.5),(491.5,508),[(491.5,508),(512,513),(542.5,471),(521,464.5)]),
                          ((493,523.5),(491.5,507.5),[(491,507.5),(512.5,513),(543,470.5),(520.5,464)])]:
        H=Hfit(Bnl,Tnl,nrm,f)
        P=backproj(np.array(top,float),nrm,1.0-H,f)
        W=(np.linalg.norm(P[1]-P[0])+np.linalg.norm(P[2]-P[3]))/2
        L=(np.linalg.norm(P[3]-P[0])+np.linalg.norm(P[2]-P[1]))/2
        print(f,'H/h=%.4f L/h=%.4f W/h=%.4f  -> at h=1.80: H=%.1f L=%.1f W=%.1f cm; at h=1.88: L=%.1f W=%.1f'%(H,L,W,H*180,L*180,W*180,L*188,W*188))
