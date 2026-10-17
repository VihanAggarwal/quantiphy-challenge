import numpy as np
class R: pass
def least_squares(fun,x0,iters=200):
    x=np.array(x0,float); lam=1e-3
    f=fun(x); cost=(f**2).sum()
    def jac(x,f):
        J=np.zeros((len(f),len(x)))
        for i in range(len(x)):
            h=1e-6*max(1,abs(x[i])); xp=x.copy(); xp[i]+=h
            J[:,i]=(fun(xp)-f)/h
        return J
    for it in range(iters):
        J=jac(x,f)
        A=J.T@J; g=J.T@f
        improved=False
        for _ in range(20):
            dx=-np.linalg.solve(A+lam*np.diag(np.diag(A)+1e-12),g)
            xn=x+dx; fn=fun(xn); cn=(fn**2).sum()
            if cn<cost:
                x,f,cost=xn,fn,cn; lam=max(lam/3,1e-9); improved=True; break
            lam*=4
        if not improved or np.abs(dx).max()<1e-10: break
    r=R(); r.x=x; r.fun=f; r.jac=jac(x,f); return r
