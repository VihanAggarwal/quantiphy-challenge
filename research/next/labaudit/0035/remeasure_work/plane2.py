import numpy as np, itertools
W='/home/user/quantiphy-challenge/research/next/labaudit/0035/remeasure_work/'
cx,cy,f=640,360,711.; Rb=0.116; k=166.1
M=np.load(W+'captured_0035bx_mask.npy')  # i,ex,ey,area,eqd,...
def u(x,y):
    v=np.array([x-cx,y-cy,f]); return v/np.linalg.norm(v)
def fitplane(X, w=None):
    c0=X.mean(0); U,S,Vt=np.linalg.svd(X-c0); n=Vt[2]
    if n@c0<0: n=-n
    return n, n@c0, S
for Rs in (0.080,0.089,0.100):
  for use_size in (True,False):
    pts=[]
    # basketball floor points (shift centre down to floor by Rb along n later) -> fit plane of centres with offsets handled iteratively
    bb=[]
    if use_size:
        for i in range(28,45):
            _,x,y,area,eqd=M[i][:5]
            uu=u(x,y); rc=k/(eqd*uu[2]**1.5); bb.append(rc*uu)
    bb.append((2.373+Rb)*u(533.4,462.0))   # basketball 1.4 s label (frame 33.6)
    so=[(2.477+Rs)*u(611.7,480.6),(2.602+Rs)*u(689.2,488.8)]
    bb=np.array(bb); so=np.array(so)
    # iterate: floor plane n.X = h ; basketball centres at h-Rb, soccer at h-Rs
    n=np.array([0.3,0.85,0.42]); n/=np.linalg.norm(n)
    for it in range(20):
        X=np.vstack([bb+Rb*n, so+Rs*n])   # project centres to floor contact points
        n,h,S=fitplane(X)
    res=np.r_[(bb+Rb*n)@n-h,(so+Rs*n)@n-h]
    # rest ball: intersect ray with plane n.X = h-Rb
    u1=u(828.7,279.9); rho1c=(h-Rb)/(n@u1); rho1s=rho1c-Rb
    # 0.9 s basketball floor-behind range: ray u2 hits floor n.X=h
    u2=u(671.3,392.7); floor_behind=h/(n@u2); centre09=(h-Rb)/(n@u2)
    print('Rs=%.3f size=%s n=%s h=%.3f sv=%s resid_rms=%.3f | rho1 centre=%.3f surf=%.3f | 0.9s centre-on-plane=%.3f floor-behind=%.3f'%(Rs,use_size,np.round(n,3),h,np.round(S,3),res.std(),rho1c,rho1s,centre09,floor_behind))
