import numpy as np, cv2
from load import frames
E=np.array([-765.,-483.]); C=np.array([1280.,720.])
_cache={}
def gray(c):
    if c not in _cache:
        _cache[c]=[cv2.GaussianBlur(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32),(3,3),0) for f in frames(c)]
    return _cache[c]
def sweep(c,p,r=12,qs=np.linspace(0.0070,0.0105,141),ref=1,fr=None,e=E):
    G=gray(c)
    if fr is None: fr=list(range(2,len(G)))
    p=np.array(p,float)
    yy,xx=np.mgrid[-r:r+1,-r:r+1].astype(np.float32)
    T=cv2.remap(G[ref],(xx+p[0]).astype(np.float32),(yy+p[1]).astype(np.float32),cv2.INTER_LINEAR)
    Tn=(T-T.mean())/ (T.std()+1e-6)
    costs=[]
    for q in qs:
        tot=0
        for i in fr:
            s=(1+q*ref)/(1+q*i)
            xi=e+(p-e)*s
            W=cv2.remap(G[i],(xi[0]+s*xx).astype(np.float32),(xi[1]+s*yy).astype(np.float32),cv2.INTER_LINEAR)
            Wn=(W-W.mean())/(W.std()+1e-6)
            tot+=np.mean((Wn-Tn)**2)
        costs.append(tot/len(fr))
    costs=np.array(costs); k=np.argmin(costs)
    # parabolic refine
    if 0<k<len(qs)-1:
        a,b,cc=costs[k-1],costs[k],costs[k+1]
        d=0.5*(a-cc)/(a-2*b+cc); qb=qs[k]+d*(qs[1]-qs[0])
    else: qb=qs[k]
    return qb,costs[k],costs
def to3d(p,q,f,vzf,ref=1,iref=24,e=E):
    p=np.array(p,float)
    s=(1+q*ref)/(1+q*iref)
    x=e+(p-e)*s
    Z=vzf*(1/q+iref)
    return np.array([(x[0]-C[0])*Z/f,(x[1]-C[1])*Z/f,Z]),x
