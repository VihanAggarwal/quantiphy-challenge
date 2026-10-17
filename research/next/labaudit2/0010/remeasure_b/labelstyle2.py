import numpy as np, sys
from dyn import *
def traj(p,t):
    tg,X,Vv=simulate(p[None,:11]); t=np.asarray(t,float)
    Xs=sample(tg,X,Vv,t)[0]
    if len(p)>=14: Xs=Xs+p[11:14][None]*t[:,None]
    return Xs
def lab(p,t_rgb,t_dep):
    Xr=traj(p,t_rgb); Xd=traj(p,t_dep)
    d=Xr/np.linalg.norm(Xr,axis=1,keepdims=True); rng=np.linalg.norm(Xd,axis=1)-R
    return rng[:,None]*d
for fn in sys.argv[1:]:
    p=np.load(fn); print(fn)
    t=np.array([15,16,17])/25.
    for kind in ['clock','depth']:
        for off in [0,0.01,0.02,0.03,0.04,0.05]:
            S=lab(p,t+(off if kind=='clock' else 0),t+off)
            v=np.linalg.norm(np.diff(S,axis=0),axis=1)*25
            print('  %s off=%.2f v(0.6)=%.3f v(0.64)=%.3f a_scalar=%.2f a_vec=%.2f'%(kind,off,v[0],v[1],(v[1]-v[0])*25,np.linalg.norm(S[2]-2*S[1]+S[0])*625))
