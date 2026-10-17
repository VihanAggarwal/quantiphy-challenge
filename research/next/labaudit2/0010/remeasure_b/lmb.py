import numpy as np
def lsqb(fun_batch,p0,iters=100,lam=1e-3,eps=None):
    """fun_batch(Pmat[B,n]) -> residuals [B,m]"""
    p=np.array(p0,float); n=len(p)
    if eps is None: eps=1e-6*np.maximum(1,np.abs(p))
    r=fun_batch(p[None])[0]; c=r@r
    for it in range(iters):
        Q=np.repeat(p[None],n,0)+np.diag(eps)
        J=((fun_batch(Q)-r[None])/eps[:,None]).T
        A=J.T@J; g=J.T@r
        lams=lam*np.array([1,4,16,64,256,1024,0.25])
        cands=[]
        for l in lams:
            try: cands.append(p-np.linalg.solve(A+l*np.diag(np.diag(A)+1e-12),g))
            except np.linalg.LinAlgError: cands.append(p)
        R=fun_batch(np.array(cands)); C=(R**2).sum(1)
        k=int(np.nanargmin(C))
        if C[k]<c:
            dp=cands[k]-p; p,r,c=cands[k],R[k],C[k]; lam=lams[k]/3
            if np.abs(dp).max()<1e-9: break
        else:
            lam*=1e4
            if lam>1e12: break
    return p,r
