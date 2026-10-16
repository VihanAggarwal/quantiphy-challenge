import cv2, numpy as np
base='/home/user/quantiphy-challenge/research/next/labaudit/0009/frames/'
rng=np.random.default_rng(0)
def fit_circle(pts):
    x,y=pts[:,0].astype(float),pts[:,1].astype(float)
    A=np.c_[2*x,2*y,np.ones_like(x)]; b=x*x+y*y
    c,_,_,_=np.linalg.lstsq(A,b,rcond=None)
    cx,cy=c[0],c[1]; r=np.sqrt(c[2]+cx*cx+cy*cy); return cx,cy,r
def ransac(pts,it=2000,tol=1.5):
    best=None;bn=0
    for _ in range(it):
        s=pts[rng.choice(len(pts),3,replace=False)]
        try: cx,cy,r=fit_circle(s)
        except: continue
        if not np.isfinite(r) or r<10 or r>200: continue
        d=np.abs(np.hypot(pts[:,0]-cx,pts[:,1]-cy)-r)
        n=(d<tol).sum()
        if n>bn: bn=n;best=(cx,cy,r)
    cx,cy,r=best
    d=np.abs(np.hypot(pts[:,0]-cx,pts[:,1]-cy)-r)
    cx,cy,r=fit_circle(pts[d<tol])
    return cx,cy,r,bn/len(pts)
out=[]
for i in range(49):
    im=cv2.imread(base+'rx_f%02d.png'%i)
    g=im.astype(int)
    mask=((255*3-g.sum(2))>60).astype(np.uint8)
    mask[680:,1000:]=0
    mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(mask)
    k=1+np.argmax(st[1:,4])
    m=(lab==k).astype(np.uint8)
    cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cs,key=cv2.contourArea)[:,0,:]
    hull=cv2.convexHull(c)[:,0,:]
    # use contour points that lie on the convex hull boundary (within 1px)
    hd=np.array([abs(cv2.pointPolygonTest(hull.reshape(-1,1,2).astype(np.float32),(float(p[0]),float(p[1])),True)) for p in c])
    pts=c[hd<1.0]
    cx,cy,r,fr=ransac(pts)
    x,y,w,h=cv2.boundingRect(m)
    out.append((i,cx,cy,r,fr,x,y,w,h,m.sum()))
    print('%2d t=%.3f cx=%7.1f cy=%7.1f r=%5.1f inl=%.2f bbox x=%d y=%d w=%d h=%d area=%d eqr=%.1f'%(i,i/24,cx,cy,r,fr,x,y,w,h,m.sum(),np.sqrt(m.sum()/np.pi)))
np.save('/home/user/quantiphy-challenge/research/next/labaudit/0009/track_x.npy',np.array(out))
