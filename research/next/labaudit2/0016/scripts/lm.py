import numpy as np
class Res: pass
def least_squares(fun,x0,iters=200):
    x=np.asarray(x0,float).copy(); lam=1e-3; r=fun(x); c=0.5*r@r
    for _ in range(iters):
        J=np.empty((r.size,x.size)); h=1e-6
        for j in range(x.size):
            dx=np.zeros_like(x); dx[j]=h*max(1,abs(x[j])); J[:,j]=(fun(x+dx)-r)/dx[j]
        A=J.T@J; g=J.T@r
        ok=False
        for _ in range(20):
            try: step=-np.linalg.solve(A+lam*np.diag(np.diag(A)+1e-12),g)
            except np.linalg.LinAlgError: lam*=10; continue
            xn=x+step; rn=fun(xn); cn=0.5*rn@rn
            if np.isfinite(cn) and cn<c: x,r,c=xn,rn,cn; lam=max(lam/3,1e-9); ok=True; break
            lam*=10
        if not ok or np.linalg.norm(step)<1e-10: break
    o=Res(); o.x=x; o.fun=r; o.cost=c; return o
