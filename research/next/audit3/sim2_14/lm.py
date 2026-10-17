import numpy as np
def lsq(res,p0,iters=200):
    p=np.array(p0,float); lam=1e-3
    r=res(p); c=r@r
    for it in range(iters):
        J=np.empty((len(r),len(p)))
        for j in range(len(p)):
            dp=np.zeros(len(p)); dp[j]=1e-5*max(1,abs(p[j]))
            J[:,j]=(res(p+dp)-r)/dp[j]
        A=J.T@J; g=J.T@r
        while True:
            step=np.linalg.solve(A+lam*np.diag(np.diag(A)+1e-12),-g)
            pn=p+step; rn=res(pn); cn=rn@rn
            if cn<c: p,r,c=pn,rn,cn; lam*=0.3; break
            lam*=10
            if lam>1e12: return p,r
    return p,r
