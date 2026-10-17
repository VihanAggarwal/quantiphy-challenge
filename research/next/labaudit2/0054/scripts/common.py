import cv2, numpy as np, os
VID='/home/user/quantiphy-challenge/data/QuantiPhy/captured_0054{}.mp4'
OUT='/home/user/quantiphy-challenge/research/next/labaudit2/0054'
SCR='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/f0054'
F=711.0; CX=640.0; CY=360.0
_cache={}
def frames(v):
    if v in _cache: return _cache[v]
    c=cv2.VideoCapture(VID.format(v)); L=[]
    while True:
        ok,f=c.read()
        if not ok: break
        L.append(f)
    _cache[v]=L; return L
def cap(k):
    """video frame index -> 25 fps capture frame index"""
    return k if k<=11 else (k+1 if k<=35 else k+2)
def tcap(k): return cap(k)/25.0
def ray(u,v,f=F):
    d=np.array([(u-CX)/f,(v-CY)/f,1.0]); return d/np.linalg.norm(d)
def bp(u,v,r,f=F): return r*ray(u,v,f)
def strip(v, ks, box, scale=2, path=None):
    x0,y0,x1,y1=box; L=frames(v); ims=[]
    for k in ks:
        im=L[k][y0:y1,x0:x1].copy()
        im=cv2.resize(im,None,fx=scale,fy=scale,interpolation=cv2.INTER_NEAREST)
        cv2.putText(im,f'{v}{k}',(3,18),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)
        ims.append(im)
    out=np.hstack(ims) if len(ims)<=6 else np.vstack([np.hstack(ims[i:i+6]+[np.zeros_like(ims[0])]*(6-len(ims[i:i+6]))) for i in range(0,len(ims),6)])
    if path: cv2.imwrite(path,out)
    return out

class _R: pass
def least_squares(fun, p0, iters=200, eps=1e-6):
    p=np.array(p0,float); lam=1e-3
    r=fun(p); cost=r@r
    for it in range(iters):
        J=np.empty((len(r),len(p)))
        for j in range(len(p)):
            dp=np.zeros_like(p); h=eps*max(1.0,abs(p[j])); dp[j]=h
            J[:,j]=(fun(p+dp)-r)/h
        A=J.T@J; gvec=J.T@r
        improved=False
        for _ in range(20):
            step=np.linalg.solve(A+lam*np.diag(np.diag(A)+1e-12),-gvec)
            pn=p+step; rn=fun(pn); cn=rn@rn
            if cn<cost:
                p,r,cost=pn,rn,cn; lam=max(lam/3,1e-12); improved=True; break
            lam*=4
        if not improved or np.linalg.norm(step)<1e-12*(1+np.linalg.norm(p)): break
    s=_R(); s.x=p; s.fun=r; return s
