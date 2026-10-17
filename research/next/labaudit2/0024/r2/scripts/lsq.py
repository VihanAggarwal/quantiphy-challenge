import numpy as np
def least_squares(fun,x0,iters=200,lam=1e-3):
    x=np.asarray(x0,float).copy(); r=fun(x); c=r@r
    for _ in range(iters):
        J=np.empty((len(r),len(x)))
        for k in range(len(x)):
            h=1e-6*max(1,abs(x[k])); xp=x.copy(); xp[k]+=h; J[:,k]=(fun(xp)-r)/h
        A=J.T@J; g=J.T@r
        while True:
            dx=-np.linalg.solve(A+lam*np.diag(np.diag(A)+1e-12),g)
            rn=fun(x+dx); cn=rn@rn
            if cn<c: x=x+dx; r=rn; lam=max(lam/3,1e-9); break
            lam*=4
            if lam>1e9: break
        if abs(c-cn)<1e-12*max(c,1e-12) or lam>1e9: c=min(c,cn); break
        c=cn
    class S: pass
    s=S(); s.x=x; s.fun=fun(x); return s
