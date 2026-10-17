import numpy as np, sys, time
from dyn import *
from lmb import lsqb
# params: 11 model + 3 pivot velocity (m/s, camera frame) + dt
wA=float(sys.argv[1]); dtfree=int(sys.argv[2]); tag=sys.argv[3]; init=sys.argv[4]
tvid=CAP/25.
def traj(Pm,t):
    tg,X,Vv=simulate(Pm[:,:11])
    Xs=sample(tg,X,Vv,t)
    return Xs+Pm[:,None,11:14]*np.asarray(t)[None,:,None]
def resid(Pm):
    Xi=traj(Pm,tvid); u,v=project(Xi)
    out=[u-U[None],v-V[None],((Pm[:,1]-638)/2.)[:,None],((Pm[:,2]-229)/2.)[:,None]]
    if wA>0:
        tg,X,Vv=simulate(Pm[:,:11]); res=[]
        for b in range(len(Pm)):
            ta=anch_t+(Pm[b,14] if dtfree else 0)
            Xa=sample(tg,X[b:b+1],Vv[b:b+1],ta)[0]+Pm[b,11:14]*ta[:,None]
            res.append((np.linalg.norm(Xa,axis=1)-R-anch_d)/0.01*wA)
        out.append(np.array(res))
    return np.concatenate(out,1)
p0=np.load(init); p0=np.concatenate([p0[:11],[0,0,0],[p0[11] if len(p0)>11 else 0.0]])
p,r=lsqb(resid,p0,iters=300)
c=(r[:2*len(U)]**2).mean()**.5
print('FINAL rms px %.3f'%c, 'params',np.round(p,5).tolist())
if wA>0: print('anchor resid (cm)',np.round(r[2*len(U)+2:]/wA,2))
np.save(f'dyn2_{tag}.npy',p)
