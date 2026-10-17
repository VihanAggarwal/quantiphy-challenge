import numpy as np
def least_squares(fun, x0, iters=300, lam=1e-3, hrel=1e-6):
    x=np.array(x0,float); r=fun(x); c=r@r
    for _ in range(iters):
        J=np.empty((len(r),len(x)))
        for j in range(len(x)):
            h=hrel*max(1.0,abs(x[j])); xp=x.copy(); xp[j]+=h; J[:,j]=(fun(xp)-r)/h
        A=J.T@J; b=J.T@r
        ok=False
        while True:
            dx=-np.linalg.solve(A+lam*np.diag(np.diag(A)+1e-12),b)
            xn=x+dx; rn=fun(xn); cn=rn@rn
            if np.isfinite(cn) and cn<c: x,r,c=xn,rn,cn; lam=max(lam/3,1e-12); ok=True; break
            lam*=4
            if lam>1e10: break
        if not ok or np.linalg.norm(dx)<1e-11*(1+np.linalg.norm(x)): break
    class S: pass
    s=S(); s.x=x; s.fun=r; s.cost=0.5*c; s.J=J; return s
