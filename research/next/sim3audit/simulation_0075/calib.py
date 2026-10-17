import cv2, numpy as np
def roadmask(im):
    im=im.astype(int); B,G,R=im[...,0],im[...,1],im[...,2]
    return ((abs(B-G)<7)&(abs(G-R)<7)&(B>120)&(B<200)).astype(np.float32)
def refine_line(mask, p1, p2, n=60, search=14, road_side=None):
    """sample along p1-p2; find road-edge transition along the normal. road_side: +1/-1 which normal side is road."""
    p1=np.array(p1,float); p2=np.array(p2,float); d=(p2-p1)/np.linalg.norm(p2-p1); nrm=np.array([-d[1],d[0]])
    sm=cv2.GaussianBlur(mask,(5,5),1.0)
    pts=[]
    for t in np.linspace(0.03,0.97,n):
        c=p1+t*(p2-p1)
        prof=[]
        ss=np.arange(-search,search+0.01,0.5)
        for s in ss:
            q=c+s*nrm
            x,y=q
            if not(1<=x<mask.shape[1]-2 and 1<=y<mask.shape[0]-2): prof.append(np.nan); continue
            prof.append(cv2.getRectSubPix(sm,(1,1),(float(x),float(y)))[0,0])
        prof=np.array(prof)
        if np.isnan(prof).any(): continue
        # road side value ~1, other ~0; find 0.5 crossing nearest centre with right orientation
        if road_side is None:
            road_side = 1 if prof[-1]>prof[0] else -1
        f=prof if road_side>0 else prof[::-1]; s2=ss if road_side>0 else ss[::-1]
        # f should go from 0 to 1; find crossing
        idx=np.where((f[:-1]<0.5)&(f[1:]>=0.5))[0]
        if len(idx)==0: continue
        i=idx[np.argmin(abs(s2[idx]))]
        s=s2[i]+(0.5-f[i])/(f[i+1]-f[i])*(s2[i+1]-s2[i])
        pts.append(c+s*nrm)
    P=np.array(pts)
    # fit line via total least squares with outlier rejection
    m=np.ones(len(P),bool)
    for it in range(5):
        mu=P[m].mean(0); U,S,Vt=np.linalg.svd(P[m]-mu); dirv=Vt[0]; nn=np.array([-dirv[1],dirv[0]])
        r=(P-mu)@nn; sd=1.4826*np.median(abs(r[m]))+0.2; m=abs(r)<3*sd
    l=np.array([nn[0],nn[1],-nn@mu])  # homogeneous line
    return l, np.sqrt(np.mean(r[m]**2)), m.sum(), len(P)
def inter(l1,l2):
    p=np.cross(l1,l2); return p[:2]/p[2]
