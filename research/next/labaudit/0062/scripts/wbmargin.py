import numpy as np
from common import *
exec(open('wbplane.py').read().split('frames=[n')[0])
def shrink(c,m):
    # move each edge inward by m px, recompute corners
    cen=c.mean(0); L=[]
    for i in range(4):
        a,b=c[i],c[(i+1)%4]; d=b-a; d/=np.linalg.norm(d); nn=np.array([-d[1],d[0]])
        if (cen-a)@nn<0: nn=-nn
        a2=a+m*nn; b2=b+m*nn; L.append(np.cross(np.r_[a2,1],np.r_[b2,1]))
    out=[]
    for i in range(4):
        p=np.cross(L[i-1],L[i]); out.append(p[:2]/p[2])
    return np.array(out)
nrm=normal(38.93,8.53)
for m in (0,1,2,3):
    S=np.array([geom(shrink(Q[n],m),nrm,1.0)[0] for n in range(20,49)])
    late=np.array([geom(shrink(Q[n],m),nrm,1.0)[0] for n in range(40,49)])
    print('shrink %dpx: all W=%.4f L=%.4f | n40-48 W=%.4f L=%.4f'%(m,(S[:,0]+S[:,2]).mean()/2,(S[:,1]+S[:,3]).mean()/2,(late[:,0]+late[:,2]).mean()/2,(late[:,1]+late[:,3]).mean()/2))
