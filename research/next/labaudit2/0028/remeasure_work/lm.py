import numpy as np
class R: pass
def least_squares(fun,p0,iters=200):
    p=np.array(p0,float); lam=1e-3
    r=fun(p); c=0.5*r@r
    for _ in range(iters):
        J=np.empty((len(r),len(p)))
        for j in range(len(p)):
            h=1e-6*max(1,abs(p[j])); q=p.copy(); q[j]+=h
            J[:,j]=(fun(q)-r)/h
        A=J.T@J; b=J.T@r
        while True:
            dp=-np.linalg.solve(A+lam*np.diag(np.diag(A)+1e-12),b)
            rn=fun(p+dp); cn=0.5*rn@rn
            if cn<c: p=p+dp; r=rn; lam=max(lam/3,1e-9); improved=c-cn; c=cn; break
            lam*=4
            if lam>1e10: improved=0; break
        if improved<1e-12: break
    o=R(); o.x=p; o.cost=c; o.fun=r; return o
