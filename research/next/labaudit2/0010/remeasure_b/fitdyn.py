import numpy as np, sys, time
from dyn import *
from lmb import lsqb
wA=float(sys.argv[1]); dtfree=int(sys.argv[2]); tag=sys.argv[3]
tvid=CAP/25.
def resid(Pm):
    # Pm[:, :11] model, Pm[:,11] = anchor time offset
    tg,X,Vv=simulate(Pm[:,:11])
    Xi=sample(tg,X,Vv,tvid); u,v=project(Xi)
    out=[u-U[None],v-V[None],((Pm[:,1]-638)/2.)[:,None],((Pm[:,2]-229)/2.)[:,None]]
    if wA>0:
        res=[]
        for b in range(len(Pm)):
            Xa=sample(tg,X[b:b+1],Vv[b:b+1],anch_t+(Pm[b,11] if dtfree else 0))[0]
            res.append((np.linalg.norm(Xa,axis=1)-R-anch_d)/0.01*wA)
        out.append(np.array(res))
    return np.concatenate(out,1)
t0=time.time()
best=None
for th0 in [0.6,0.8]:
  for ph0 in np.linspace(-np.pi,np.pi,8,endpoint=False):
    p0=np.array([1.514,638,229,0.35,0.42,1.2,th0,ph0,0.,0.,0.05,0.0])
    p,r=lsqb(resid,p0,iters=40)
    c=(r[:2*len(U)]**2).mean()**.5
    if best is None or c<best[0]: best=(c,p)
print('init search done',time.time()-t0, best[0]); sys.stdout.flush()
p,r=lsqb(resid,best[1],iters=300)
c=(r[:2*len(U)]**2).mean()**.5
print('FINAL rms px %.3f'%c, 'params',np.round(p,5).tolist())
if wA>0: print('anchor resid (cm)',np.round(r[2*len(U)+2:]/wA,2))
np.save(f'dyn_{tag}.npy',p)
