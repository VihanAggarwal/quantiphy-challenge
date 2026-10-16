import numpy as np, json
from lm import lsq
cx=640.; cy=360.
C=json.load(open('board_corners_o.json'))
frames=[k for k in sorted(C,key=int) if 20<=int(k)<=48]
Qs=[np.array(C[k]) for k in frames]
def nvec(a,b):
    # n parametrized by two angles: roll a, pitch b
    return np.array([np.sin(a)*np.cos(b), np.cos(a)*np.cos(b), np.sin(b)])
def bp(Q,n,f):
    r=np.c_[(Q[:,0]-cx)/f,(Q[:,1]-cy)/f,np.ones(len(Q))]
    return r/(r@n)[:,None]
def res(x,fixf=None):
    a,b,L,W=x[:4]; f=fixf if fixf else x[4]
    n=nvec(a,b); R=[]
    for Q in Qs:
        X=bp(Q,n,f)
        s=[np.linalg.norm(X[(k+1)%4]-X[k]) for k in range(4)]
        dg=[np.linalg.norm(X[2]-X[0]),np.linalg.norm(X[3]-X[1])]
        D=np.hypot(L,W)
        R+= [ (s[0]-L)/L,(s[2]-L)/L,(s[1]-W)/W,(s[3]-W)/W,(dg[0]-D)/D,(dg[1]-D)/D ]
    return np.array(R)
x0=[-0.17,0.69,0.46,0.33]
for fixf in [711.,None]:
    xx=x0+([] if fixf else [711.])
    xs,fun=lsq(lambda x:res(x,fixf),xx,huber=0.03)
    class S: pass
    sol=S(); sol.x=xs; sol.fun=fun
    a,b,L,W=sol.x[:4]; n=nvec(a,b)
    print('fixf',fixf,'f',sol.x[4] if not fixf else fixf,'n',np.round(n,4),'L/h',round(L,4),'W/h',round(W,4),'aspect',round(L/W,3),'rms',round(np.sqrt(np.mean(sol.fun**2)),4))
    np.save('n_fit_%s.npy'%('711' if fixf else 'free'),np.r_[n,L,W,(sol.x[4] if not fixf else fixf)])
    # per-frame sizes with this n
    f=sol.x[4] if not fixf else fixf
    for k,Q in zip(frames,Qs):
        X=bp(Q,n,f); s=[np.linalg.norm(X[(j+1)%4]-X[j]) for j in range(4)]
        print('  ',k,np.round(s,3))
