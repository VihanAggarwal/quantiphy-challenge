import cv2, numpy as np
def bilinear(g,x,y):
    return cv2.remap(g,np.float32(x).reshape(1,-1),np.float32(y).reshape(1,-1),cv2.INTER_LINEAR).ravel()
def edge_line(g,p,q,trim=(0.15,0.85),half=10,inside_sign=None,frac=0.5,step=1.0):
    """g float gray; p,q approx endpoints. sample perpendicular profiles; find crossing at frac between
    the two plateau levels; return (point,dir) fitted line and pts"""
    p=np.array(p,float); q=np.array(q,float); d=q-p; L=np.linalg.norm(d); d/=L; nrm=np.array([-d[1],d[0]])
    pts=[]
    for s in np.arange(trim[0]*L,trim[1]*L,step):
        c=p+s*d
        t=np.arange(-half,half+0.01,0.25)
        xs=c[0]+t*nrm[0]; ys=c[1]+t*nrm[1]
        prof=bilinear(g,xs,ys)
        a=np.median(prof[:12]); b=np.median(prof[-12:])
        if abs(a-b)<40: continue
        lev=a+frac*(b-a) if b>a else b+(1-frac)*(a-b)
        # crossing nearest to center
        sgn=np.sign(prof-lev); idx=np.where(np.diff(sgn)!=0)[0]
        if len(idx)==0: continue
        k=idx[np.argmin(np.abs(t[idx]))]
        t0=t[k]+(lev-prof[k])/(prof[k+1]-prof[k])*(t[k+1]-t[k])
        pts.append(c+t0*nrm)
    pts=np.array(pts)
    vx,vy,x0,y0=cv2.fitLine(pts.astype(np.float32),cv2.DIST_HUBER,0,0.01,0.01).ravel()
    line=np.cross([x0,y0,1.],[x0+vx,y0+vy,1.])
    res=(np.c_[pts,np.ones(len(pts))]@line)/np.hypot(line[0],line[1])
    return line,pts,res
def inter(l1,l2):
    X=np.cross(l1,l2); return X[:2]/X[2]
