import numpy as np
def lsq(fun,x0,iters=200,huber=None):
    x=np.array(x0,float); lam=1e-3
    def cost(x):
        r=fun(x)
        if huber:
            a=np.abs(r); w=np.where(a<huber,1,huber/a); return r*np.sqrt(w)
        return r
    r=cost(x); c=r@r
    for it in range(iters):
        J=np.zeros((len(r),len(x)))
        for j in range(len(x)):
            dx=np.zeros(len(x)); dx[j]=1e-6*max(1,abs(x[j]))
            J[:,j]=(cost(x+dx)-r)/dx[j]
        A=J.T@J; g=J.T@r
        while True:
            step=np.linalg.solve(A+lam*np.diag(np.diag(A)+1e-12),-g)
            xn=x+step; rn=cost(xn); cn=rn@rn
            if cn<c: x,r,c=xn,rn,cn; lam=max(lam/3,1e-9); break
            lam*=4
            if lam>1e9: return x,fun(x)
        if np.linalg.norm(step)<1e-10: break
    return x,fun(x)
