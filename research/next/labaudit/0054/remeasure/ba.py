import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure')
import numpy as np, cv2
from pts import *
FA=711.0; C=np.array([640.,360.])
def rot(rv): return cv2.Rodrigues(np.asarray(rv,float).reshape(3,1))[0]
def build(excl=()):
    A=[];B=[];lab=[]
    for nm,da,db in [('W',aW,bW),('G',aG,bG)]:
        for k in sorted(set(da)&set(db)):
            if (nm,k) in excl or k in excl: continue
            A.append(da[k]);B.append(db[k]);lab.append((nm,k))
    return np.array(A,float),np.array(B,float),lab
def proj(X,f): return f*X[:,:2]/X[:,2:3]+C
def Kmat(f): return np.array([[f,0,C[0]],[0,f,C[1]],[0,0,1.]])
def tri(xa,xb,R,t,fb,fa=FA):
    Pa=Kmat(fa)@np.hstack([np.eye(3),np.zeros((3,1))]); Pb=Kmat(fb)@np.hstack([R,t.reshape(3,1)])
    X=[]
    for (u1,v1),(u2,v2) in zip(xa,xb):
        M=np.array([u1*Pa[2]-Pa[0],v1*Pa[2]-Pa[1],u2*Pb[2]-Pb[0],v2*Pb[2]-Pb[1]])
        M/=np.linalg.norm(M[:,:3],axis=1,keepdims=True)
        _,_,vt=np.linalg.svd(M); x=vt[-1]; X.append(x[:3]/x[3])
    return np.array(X)
def tdir(p):
    th,ph=p; return np.array([np.sin(th)*np.cos(ph),np.sin(th)*np.sin(ph),np.cos(th)])
def unpack(p,fb_fixed):
    R=rot(p[:3]); t=tdir(p[3:5]); fb=p[5] if fb_fixed is None else fb_fixed
    return R,t,fb
def resid(p,xa,xb,fb_fixed=None,fa=FA):
    R,t,fb=unpack(p,fb_fixed)
    X=tri(xa,xb,R,t,fb,fa)
    # refine each point a few GN steps on reprojection
    for it in range(3):
        for j in range(len(X)):
            def r1(Xj):
                return np.concatenate([proj(Xj[None],fa)[0]-xa[j],proj((R@Xj+t)[None],fb)[0]-xb[j]])
            J=np.zeros((4,3)); r0=r1(X[j])
            for q in range(3):
                d=np.zeros(3); d[q]=1e-6*max(1,abs(X[j][q])); J[:,q]=(r1(X[j]+d)-r0)/d[q]
            X[j]=X[j]-np.linalg.lstsq(J,r0,rcond=None)[0]
    ra=proj(X,fa)-xa; rb=proj(X@R.T+t,fb)-xb
    return np.concatenate([ra.ravel(),rb.ravel()]),X
def lm(fun,p,iters=60):
    lam=1e-3
    r=fun(p); cost=(r**2).sum()
    for it in range(iters):
        J=np.zeros((len(r),len(p)))
        for q in range(len(p)):
            d=np.zeros(len(p)); d[q]=1e-6*max(1,abs(p[q])); J[:,q]=(fun(p+d)-r)/d[q]
        A=J.T@J; g=J.T@r
        while True:
            dp=-np.linalg.solve(A+lam*np.diag(np.diag(A)+1e-12),g)
            r2=fun(p+dp); c2=(r2**2).sum()
            if c2<cost: p=p+dp; r=r2; lam=max(lam/3,1e-9); break
            lam*=5
            if lam>1e8: return p,r
        if abs(cost-c2)<1e-10*cost: cost=c2; break
        cost=c2
    return p,r
def solve(xa,xb,fb0=711.,fit_fb=True,fa=FA):
    na=(xa-C)/fa; nb=(xb-C)/fb0
    E,mask=cv2.findEssentialMat(na,nb,np.eye(3),method=cv2.LMEDS)
    _,R,t,_=cv2.recoverPose(E,na,nb,np.eye(3))
    t=t.ravel(); th=np.arccos(t[2]); ph=np.arctan2(t[1],t[0])
    p0=np.concatenate([cv2.Rodrigues(R)[0].ravel(),[th,ph]]+([[fb0]] if fit_fb else []))
    fun=lambda p: resid(p,xa,xb,None if fit_fb else fb0,fa)[0]
    p,r=lm(fun,p0)
    R,t,fb=unpack(p,None if fit_fb else fb0)
    res,X=resid(p,xa,xb,None if fit_fb else fb0,fa)
    return R,t,fb,X,res.reshape(-1,2)
if __name__=='__main__':
    xa,xb,lab=build()
    n=len(xa)
    for fit in [False,True]:
        R,t,fb,X,res=solve(xa,xb,fit_fb=fit)
        print('fit_fb',fit,'fb=%.1f'%fb,'rms a=%.2f b=%.2f px'%(np.sqrt((res[:n]**2).sum(1).mean()),np.sqrt((res[n:]**2).sum(1).mean())))
        print(' Rvec(deg)',np.degrees(cv2.Rodrigues(R)[0].ravel()).round(2),'tdir',t.round(3))
        for (nm,k),ra,rb in zip(lab,res[:n],res[n:]): print('  ',nm,k,ra.round(1),rb.round(1))
