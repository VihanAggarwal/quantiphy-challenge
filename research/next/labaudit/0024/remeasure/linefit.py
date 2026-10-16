import cv2, numpy as np
def map_coordinates(g, yx, order=1):
    y=np.asarray(yx[0],float); x=np.asarray(yx[1],float)
    x0=np.floor(x).astype(int); y0=np.floor(y).astype(int); fx=x-x0; fy=y-y0
    return (g[y0,x0]*(1-fx)*(1-fy)+g[y0,x0+1]*fx*(1-fy)+g[y0+1,x0]*(1-fx)*fy+g[y0+1,x0+1]*fx*fy)
D='/home/user/quantiphy-challenge/research/next/labaudit/0024/remeasure/'
def load(name, chan='gray'):
    f=cv2.imread(D+name).astype(float)
    if chan=='gray': g=f.mean(axis=2)
    elif chan=='rb': g=f[:,:,2]-f[:,:,0]
    elif chan in 'bgr': g=f[:,:,'bgr'.index(chan)]
    return cv2.GaussianBlur(g,(0,0),0.8)
def fitline(g, p0, p1, half=6, n=40, trim=0.1, sign=0, verbose=False):
    p0=np.array(p0,float); p1=np.array(p1,float)
    d=p1-p0; L=np.linalg.norm(d); t=d/L; nrm=np.array([-t[1],t[0]])
    pts=[]
    for s in np.linspace(trim,1-trim,n):
        c=p0+s*d
        offs=np.arange(-half,half+0.01,0.25)
        xy=c[None,:]+offs[:,None]*nrm[None,:]
        prof=map_coordinates(g,[xy[:,1],xy[:,0]],order=1)
        der=np.gradient(prof)
        if sign==0: der=np.abs(der)
        else: der=sign*der
        k=np.argmax(der)
        if 0<k<len(der)-1:
            a,b,cc=der[k-1],der[k],der[k+1]; den=a-2*b+cc
            off=0.5*(a-cc)/den if den!=0 else 0
        else: off=0
        o=offs[k]+off*0.25
        pts.append(c+o*nrm)
    pts=np.array(pts)
    # robust fit: total least squares with iterative trimming
    keep=np.ones(len(pts),bool)
    for it in range(3):
        m=pts[keep].mean(0); u,s,vt=np.linalg.svd(pts[keep]-m); dirv=vt[0]; nv=vt[1]
        r=(pts-m)@nv
        sd=np.std(r[keep])
        keep=np.abs(r)<max(2.5*sd,0.3)
    if verbose: print('resid sd %.3f kept %d/%d'%(np.std(r[keep]),keep.sum(),len(pts)))
    # homogeneous line
    l=np.array([nv[0],nv[1],-nv@m])
    return l, pts, np.std(r[keep])
def inter(l1,l2):
    p=np.cross(l1,l2); return p[:2]/p[2]
