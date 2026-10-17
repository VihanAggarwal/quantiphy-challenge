# 3D ballistic fit with gravity = 980 cm/s^2 along -table normal; capture clock 25 fps
import numpy as np, sys

sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0033/scripts')
from geo import *
def fit(frames, R='x', f=711, mapping=cap, key=('cx','cy'), g=980., fps=25.):
    P=pose(f); T=load_track(R)
    ks=[k for k in frames if k in T]
    t=np.array([mapping(k) for k in ks],float)/fps
    uv=np.array([[T[k][key[0]],T[k][key[1]]] for k in ks])
    gv=-g*P['n']
    t0=t.mean()
    def model(p):
        X0=p[:3]; V0=p[3:6]; dt=(t-t0)[:,None]
        return X0+V0*dt+0.5*gv*dt**2
    def res(p): return (project(model(p),f)-uv).ravel()
    # init: depth 120
    best=None
    for z0 in [60,100,150,200]:
        r0=ray(uv.mean(0)[0],uv.mean(0)[1],f)*z0
        p0=np.r_[r0,0,0,0]
        s=least_squares(res,p0)
        if best is None or s.cost<best.cost: best=s
    p=best.x; X=model(p); rms=np.sqrt(np.mean(best.fun**2))
    return dict(p=p,t=t,t0=t0,ks=ks,X=X,rms=rms,res=best.fun.reshape(-1,2),P=P,gv=gv)
if __name__=='__main__':
    for R in ['x','s']:
     for f in [711,740]:
      for name,fr in [('arc1',range(5,14)),('arc2',range(16,24))]:
        for mname,mp in [('drop12,36',cap),('nodrop25',lambda k:k),('24fps',lambda k:k*25/24)]:
            r=fit(list(fr),R,f,mp)
            X=r['X']; rng=np.linalg.norm(X,axis=1)
            V=r['p'][3:6]
            print(R,f,name,mname,'rms %.2f'%r['rms'],'range %.1f..%.1f'%(rng[0],rng[-1]),'V0(t0) %s'%np.round(V,1),'t0 c%.2f'%(r['t0']*25))
