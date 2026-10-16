import numpy as np
def least_squares(fun,x0,iters=200):
    x=np.array(x0,float);lam=1e-3
    r=fun(x);cost=0.5*r@r
    for it in range(iters):
        J=np.empty((len(r),len(x)))
        for j in range(len(x)):
            h=1e-6*max(1,abs(x[j])); xp=x.copy();xp[j]+=h
            J[:,j]=(fun(xp)-r)/h
        A=J.T@J;g=J.T@r
        while True:
            try: dx=-np.linalg.solve(A+lam*np.diag(np.diag(A)+1e-12),g)
            except np.linalg.LinAlgError: lam*=10;continue
            xn=x+dx;rn=fun(xn);cn=0.5*rn@rn
            if cn<cost: x,r,cost=xn,rn,cn;lam=max(lam/3,1e-9);break
            lam*=4
            if lam>1e12: break
        if lam>1e12 or np.linalg.norm(dx)<1e-10: break
    class R: pass
    o=R();o.x=x;o.cost=cost;return o
