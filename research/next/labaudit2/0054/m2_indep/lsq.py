import numpy as np
class R: pass
def least_squares(fun,x0,iters=200,eps=1e-6):
    x=np.array(x0,float); lam=1e-3
    r=fun(x); c=r@r
    for it in range(iters):
        J=np.empty((len(r),len(x)))
        for k in range(len(x)):
            dx=np.zeros_like(x); h=eps*max(1,abs(x[k])); dx[k]=h
            J[:,k]=(fun(x+dx)-r)/h
        A=J.T@J; g=J.T@r
        while True:
            step=np.linalg.solve(A+lam*np.diag(np.diag(A)+1e-12),-g)
            xn=x+step; rn=fun(xn); cn=rn@rn
            if cn<c: x,r,c=xn,rn,cn; lam=max(lam/3,1e-9); break
            lam*=4
            if lam>1e12: break
        if lam>1e12 or np.linalg.norm(step)<1e-10: break
    s=R(); s.x=x; s.fun=r; s.cost=c; s.jac=J; return s
