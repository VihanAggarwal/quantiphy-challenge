import numpy as np, json, cv2
BASE='/home/user/quantiphy-challenge/research/next/labaudit2/0033/'
C=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0033/corners.json'))
CORN=np.array([C['FL'],C['FR'],C['NL'],C['NR']],float)
def cap(k):  # video frame -> capture frame (25 fps)
    return k + (k>=12) + (k>=36)
def pose(f, W=60.3, D=76.0):
    K=np.array([[f,0,640],[0,f,360],[0,0,1.]])
    obj=np.array([[0,D,0],[W,D,0],[0,0,0],[W,0,0]],float)
    ok,rv,tv=cv2.solvePnP(obj,CORN,K,None,flags=cv2.SOLVEPNP_IPPE)
    Rm,_=cv2.Rodrigues(rv)
    n=Rm[:,2].copy()          # table 'up' (z) axis in camera coords
    d=float(n@tv.ravel())     # plane: n.X = d  (X camera coords, cm); camera height = -d
    return dict(K=K,R=Rm,t=tv.ravel(),n=n,d=d,h=-d,f=f)
def ray(u,v,f):
    r=np.array([(u-640)/f,(v-360)/f,1.0]); return r/np.linalg.norm(r)
def on_plane(u,v,P,height):
    # intersect ray with plane at 'height' cm above the top (n.X = d + height)
    r=ray(u,v,P['f']); s=(P['d']+height)/(P['n']@r); return s*r
def project(X,f):
    return np.array([f*X[...,0]/X[...,2]+640, f*X[...,1]/X[...,2]+360]).T
def load_track(R='x'):
    T=json.load(open(BASE+'track_%s.json'%R)); out={}
    for e in T:
        if e is None: continue
        out[e['f']]=e
    return out
class _Res:
    pass
def least_squares(fun, x0, iters=200, eps=1e-6):
    """Small Levenberg-Marquardt with numeric Jacobian (no scipy available)."""
    x=np.array(x0,float); lam=1e-3
    r=fun(x); cost=0.5*r@r
    for it in range(iters):
        J=np.empty((r.size,x.size))
        for j in range(x.size):
            dx=np.zeros_like(x); h=eps*max(1.0,abs(x[j])); dx[j]=h
            J[:,j]=(fun(x+dx)-r)/h
        A=J.T@J; gr=J.T@r
        improved=False
        for _ in range(20):
            step=np.linalg.solve(A+lam*np.diag(np.diag(A)+1e-12),-gr)
            xn=x+step; rn=fun(xn); cn=0.5*rn@rn
            if cn<cost:
                x,r,cost=xn,rn,cn; lam=max(lam/3,1e-12); improved=True; break
            lam*=4
        if not improved or np.linalg.norm(step)<1e-10*(1+np.linalg.norm(x)): break
    o=_Res(); o.x=x; o.fun=r; o.cost=cost; return o
