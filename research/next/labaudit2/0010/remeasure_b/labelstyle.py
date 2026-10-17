import numpy as np, sys
from dyn import *
def traj(p,t):
    tg,X,Vv=simulate(p[None,:11]); t=np.asarray(t,float)
    Xs=sample(tg,X,Vv,t)[0]
    if len(p)>=14: Xs=Xs+p[11:14][None]*t[:,None]
    return Xs
for fn in sys.argv[1:]:
    p=np.load(fn)
    print(fn, 'L=%.4f pivot range=%.3f'%(p[3],p[0]))
    for dt in [0.0,0.01,0.02,0.03,0.04]:
        caps=np.array([15,16,17]); t=caps/25.
        Xr=traj(p,t)           # RGB-time centre (for ray direction)
        Xd=traj(p,t+dt)        # depth-time centre
        d=Xr/np.linalg.norm(Xr,axis=1,keepdims=True)
        rng=np.linalg.norm(Xd,axis=1)-R
        S=rng[:,None]*d
        v=np.linalg.norm(np.diff(S,axis=0),axis=1)*25
        a_s=(v[1]-v[0])*25; a_v=np.linalg.norm(S[2]-2*S[1]+S[0])*625
        print('  dt=%.2f ranges %s  v15=%.3f v16=%.3f  a_scalar=%.2f a_vec=%.2f'%(dt,np.round(rng,4),v[0],v[1],a_s,a_v))
    # physical
    tt=np.array([0.6-1e-3,0.6,0.6+1e-3]); X=traj(p,tt)
    vel=(X[2]-X[0])/2e-3; acc=(X[2]-2*X[1]+X[0])/1e-6
    print('  physical t=0.6: |v|=%.3f |a|=%.3f tangential=%.3f'%(np.linalg.norm(vel),np.linalg.norm(acc),acc@vel/np.linalg.norm(vel)))
