import sys; sys.path.insert(0,'scripts')
from geo import *
pts=[('book',666.4,617.9,2.082,0.018),('cup',564.3,424.0,2.516,0.06),('ball',985.8,369.6,2.925,0.116),
     ('wb62',705.4,415.3,2.815,0.008),('bag62',837.3,329.1,3.307,0.01)]
def nvec(a,b): return np.array([np.sin(b)*np.cos(a), np.cos(b)*np.cos(a), np.sin(a)])
A=np.radians(np.arange(25,45,0.1)); B=np.radians(np.arange(-20,15,0.1))
for mode in ['range','zdepth']:
  for f in (711,):
    X=[]
    for nm,u,v,r,zz in pts:
        d=np.array([(u-CX)/f,(v-CY)/f,1.0])
        if mode=='range': p=r*d/np.linalg.norm(d)
        else: p=r*d
        if nm=='ball': p=p+0.116*d/np.linalg.norm(d)
        X.append(p)
    X=np.array(X); z=np.array([p[4] for p in pts])
    for sel,name in [([0,1,2,3,4],'all5'),([0,1,3,4],'no ball'),([0,3,4],'flat')]:
        best=None
        for a in A:
            for b in B:
                n=nvec(a,b); h=X[sel]@n+z[sel]; H=h.mean(); r=((h-H)**2).sum()
                if best is None or r<best[0]: best=(r,a,b,H)
        r,a,b,H=best; n=nvec(a,b)
        print(mode,f,'%-8s pitch %.1f roll %.1f H %.3f'%(name,90-np.degrees(np.arccos(n[2])),np.degrees(b),H),'resid cm',np.round((H-X@n-z)*100,1))
