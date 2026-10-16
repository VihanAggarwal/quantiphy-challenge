import numpy as np
class R: pass
def least_squares(fun,x0,iters=200):
    x=np.array(x0,float); lam=1e-3
    r=fun(x); c=0.5*r@r
    for _ in range(iters):
        J=np.zeros((len(r),len(x)))
        for j in range(len(x)):
            dx=np.zeros_like(x); dx[j]=1e-6*max(1,abs(x[j])); J[:,j]=(fun(x+dx)-r)/dx[j]
        A=J.T@J; b=J.T@r
        while True:
            step=np.linalg.solve(A+lam*np.diag(np.diag(A)+1e-12),-b)
            xn=x+step; rn=fun(xn); cn=0.5*rn@rn
            if cn<c: x,r,c=xn,rn,cn; lam=max(lam/3,1e-9); break
            lam*=4
            if lam>1e9: break
        if np.linalg.norm(step)<1e-10 or lam>1e9: break
    o=R(); o.x=x; o.fun=r; o.cost=c; return o
