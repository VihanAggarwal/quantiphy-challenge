import numpy as np, json, sys
from dyn import *
use_anch=int(sys.argv[1]) if len(sys.argv)>1 else 0
tvid=CAP/25.
def resid(p):
    dt0=p[-1]
    X,_=simulate(p,np.concatenate([tvid,anch_t+dt0]))
    Xi=X[:len(tvid)]; u,v=project(Xi)
    r=[u-U,v-V]
    if use_anch:
        Xa=X[len(tvid):]; rng=np.linalg.norm(Xa,axis=1)-R
        r.append((rng-anch_d)/0.01*use_anch)   # 1 cm ~ 1 px weight
    return np.concatenate(r)
# init
p0=np.array([1.514,638,229,0.35,0.42,1.2,0.7,np.pi/2,0.,0.,0.05,0.0])
best=None
for th0 in [0.6,0.75]:
  for ph0 in [np.pi/2,-np.pi/2,0.0,np.pi]:
    p0[6]=th0;p0[7]=ph0
    try:
        p,r=lsq(resid,p0,iters=60)
    except Exception as e:
        continue
    c=(r[:2*len(U)]**2).mean()**.5
    print('init',th0,ph0,'rms px',round(c,3),np.round(p,4)); sys.stdout.flush()
    if best is None or c<best[0]: best=(c,p)
p,r=lsq(resid,best[1],iters=300)
print('FINAL rms px',(r[:2*len(U)]**2).mean()**.5, np.round(p,5))
np.save('dynfit_anch%d.npy'%use_anch,p)
