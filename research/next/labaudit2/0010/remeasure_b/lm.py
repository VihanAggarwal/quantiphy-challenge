import numpy as np
def lsq(fun,p0,iters=200,lam=1e-3):
    p=np.array(p0,float); r=fun(p); c=r@r
    for it in range(iters):
        J=np.empty((len(r),len(p)))
        for k in range(len(p)):
            h=1e-6*max(1,abs(p[k])); q=p.copy(); q[k]+=h; J[:,k]=(fun(q)-r)/h
        A=J.T@J; g=J.T@r
        while True:
            dp=-np.linalg.solve(A+lam*np.diag(np.diag(A)+1e-12),g)
            q=p+dp; rq=fun(q); cq=rq@rq
            if cq<c: p,r,c=q,rq,cq; lam=max(lam/3,1e-9); break
            lam*=4
            if lam>1e9: return p,r
        if np.abs(dp).max()<1e-10: break
    return p,r
