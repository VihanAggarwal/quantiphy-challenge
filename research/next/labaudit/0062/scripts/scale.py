import numpy as np, json
from common import *
exec(open('wbplane.py').read().split('frames=[n')[0])  # reuse Q, normal, geom, backproj
import sys
for f,(p,r) in {700:(39.34,8.43),711:(38.93,8.53),722:(38.50,8.66)}.items():
    nrm=normal(p,r)
    print('=== f',f,'normal',np.round(nrm,4))
    # board centre (intersection of diagonals of quad == projective centre) in image
    def ctr(c):
        l1=np.cross(np.r_[c[0],1],np.r_[c[2],1]); l2=np.cross(np.r_[c[1],1],np.r_[c[3],1]); p_=np.cross(l1,l2); return p_[:2]/p_[2]
    for n in (33,34,35):
        c=ctr(Q[n]); d=np.r_[(c-[CX,CY])/f,1]; dh=d/np.linalg.norm(d)
        h=2.815*(dh@nrm)
        print(' board n%d centre %s  h_from_2.815=%.3f'%(n,np.round(c,1),h))
    for name,uv,rng in [('bag',(837.4,329.2),3.307),('box',(516.8,495.5),2.082),('mario',(635.1,623.8),2.016),('bin',(337.9,156.1),2.303)]:
        d=np.r_[(np.array(uv)-[CX,CY])/f,1]; dh=d/np.linalg.norm(d)
        print(' %s h_from_stated=%.3f (if centre on floor)'%(name,rng*(dh@nrm)))
    # velocity: board centre on plane per frame (h=1)
    tc=lambda n: n/25 if n<=11 else ((n+1)/25 if n<=35 else (n+2)/25)
    P={n:backproj(ctr(Q[n])[None],nrm,1.0,f)[0] for n in range(20,49)}
    for n in range(28,40):
        v=np.linalg.norm(P[n+1]-P[n])/(tc(n+1)-tc(n)); v24=np.linalg.norm(P[n+1]-P[n])*24
        print('  n%d->%d  v(h=1)=%.3f /s (cap timing)  %.3f (24fps)'%(n,n+1,v,v24))
