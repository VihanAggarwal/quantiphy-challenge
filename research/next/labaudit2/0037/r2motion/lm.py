import numpy as np
class R: pass
def least_squares(fun,p0,iters=200):
    p=np.array(p0,float); lam=1e-3
    r=fun(p); cost=r@r
    for it in range(iters):
        J=np.empty((len(r),len(p)))
        for j in range(len(p)):
            h=1e-6*max(1,abs(p[j])); q=p.copy(); q[j]+=h; J[:,j]=(fun(q)-r)/h
        A=J.T@J; g=J.T@r
        while True:
            dp=-np.linalg.solve(A+lam*np.diag(np.diag(A)+1e-12),g)
            rn=fun(p+dp); cn=rn@rn
            if cn<cost:
                p=p+dp; r=rn; lam=max(lam/3,1e-9); done=abs(cost-cn)<1e-12*max(cost,1e-12); cost=cn; break
            lam*=4
            if lam>1e12: done=True; break
        if done: break
    o=R(); o.x=p; o.fun=r; o.J=J; return o
