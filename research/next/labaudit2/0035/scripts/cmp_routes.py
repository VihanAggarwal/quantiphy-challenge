# per-frame comparison of size-based and plane-based centre ranges
import sys
from geom import *
from stated_plane import pts
take=sys.argv[1]; f=float(sys.argv[2]); swap=len(sys.argv)>3 and sys.argv[3]=='swap'
tr=load_tr(take)
P=pts(take,f,swap=swap)
n=np.array([0,-0.8,-0.6])
for it in range(10):
    Q=np.array([p[6]+(0.116-p[3])*n for p in P]); n,hc=fit_plane(Q)
h=hc+0.116
print('plane n',np.round(n,3),'h %.3f'%h)
# size K: calibrate each ball on its stated labels (mean of the K values)
for key,R in [('bb',0.116),('sb',0.089)]:
    Ks=[]
    for p in P:
        if p[0]!=key: continue
        c=p[1]
        d=capframe_pos(tr[key],int(c)) if c==int(c) else {kk:(capframe_pos(tr[key],int(c))[kk]+capframe_pos(tr[key],int(c)+1)[kk])/2 for kk in ['cx','cy','deq','minor']}
        Ks.append((p[2]+R)*d['deq']*cosa(d['cx'],d['cy'],f)**1.5)
    print(key,'K from labels',np.round(Ks,1))
    K=np.mean(Ks)
    line=[]
    for k in sorted(tr[key]):
        d=tr[key][k]
        rs=size_range(d,K,f=f); rp=np.linalg.norm(plane_point(d['cx'],d['cy'],n,h,R,f))
        line.append(f'{k}:{rs/rp:.3f}')
    print(' size/plane per video frame:',' '.join(line))
