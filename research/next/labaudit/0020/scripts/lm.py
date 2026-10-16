import numpy as np
class R: pass
def least_squares(fun,x0,iters=200,eps=1e-6):
    x=np.asarray(x0,float).copy(); lam=1e-3
    r=fun(x); c=0.5*r@r
    for _ in range(iters):
        J=np.empty((len(r),len(x)))
        for k in range(len(x)):
            dx=np.zeros_like(x); h=eps*max(1,abs(x[k])); dx[k]=h
            J[:,k]=(fun(x+dx)-r)/h
        A=J.T@J; g=J.T@r
        improved=False
        for _ in range(20):
            try: step=-np.linalg.solve(A+lam*np.diag(np.diag(A)+1e-12),g)
            except np.linalg.LinAlgError: lam*=10; continue
            xn=x+step; rn=fun(xn); cn=0.5*rn@rn
            if cn<c:
                x,r,c=xn,rn,cn; lam=max(lam/3,1e-9); improved=True; break
            lam*=5
        if not improved or np.linalg.norm(step)<1e-10: break
    o=R(); o.x=x; o.cost=c; o.fun=r; return o
