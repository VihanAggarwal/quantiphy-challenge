import numpy as np
class R: pass
def least_squares(fun,x0,iters=200):
    x=np.array(x0,float)
    lam=1e-3
    for _ in range(iters):
        r=fun(x); J=np.zeros((len(r),len(x)))
        for k in range(len(x)):
            h=1e-6*max(1,abs(x[k])); xp=x.copy(); xp[k]+=h; J[:,k]=(fun(xp)-r)/h
        A=J.T@J; g=J.T@r
        dx=-np.linalg.solve(A+lam*np.diag(np.diag(A)+1e-12),g)
        if np.sum(fun(x+dx)**2)<np.sum(r**2): x=x+dx; lam*=0.3
        else: lam*=10
        if np.linalg.norm(dx)<1e-9*(1+np.linalg.norm(x)): break
    o=R(); o.x=x; return o
