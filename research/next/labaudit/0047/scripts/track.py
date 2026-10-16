import cv2, numpy as np, json, sys
D='/home/user/quantiphy-challenge/research/next/labaudit/0047/'
F=711.0; CX=640.0; CY=360.0
def rays(px,py,f=F):
    v=np.stack([(px-CX)/f,(py-CY)/f,np.ones_like(px,dtype=float)],1)
    return v/np.linalg.norm(v,axis=1,keepdims=True)
def fit_cone(pts,c0,a0,f=F,iters=30):
    """fit unit centre direction c and half angle a to boundary rays; robust (Huber-ish reweight)"""
    d=rays(pts[:,0],pts[:,1],f)
    c=c0/np.linalg.norm(c0); a=a0
    w=np.ones(len(d))
    for it in range(iters):
        # Gauss-Newton on params (theta,phi of c, a)
        def res(c,a): return np.arccos(np.clip(d@c,-1,1))-a
        r=res(c,a)
        s=1.4826*np.median(np.abs(r))+1e-6
        w=np.where(np.abs(r)<2.5*s,1.0,0.0)
        # numeric jacobian over small perturbations: param x = (ex,ey,a) tangent perturbations
        e1=np.cross(c,[0,1,0]); e1/=np.linalg.norm(e1); e2=np.cross(c,e1)
        J=np.zeros((len(d),3)); h=1e-5
        for k,(dc,da) in enumerate([(e1*h,0),(e2*h,0),(0*e1,h)]):
            cc=c+dc; cc/=np.linalg.norm(cc)
            J[:,k]=(res(cc,a+da)-r)/h
        W=w[:,None]
        dx=np.linalg.lstsq(J*W,-(r*w),rcond=None)[0]
        c=c+dx[0]*e1+dx[1]*e2; c/=np.linalg.norm(c); a+=dx[2]
        if np.abs(dx).max()<1e-9: break
    r=res(c,a)
    return c,a,r,w
def proj(c,f=F):
    return np.array([CX+f*c[0]/c[2],CY+f*c[1]/c[2]])
