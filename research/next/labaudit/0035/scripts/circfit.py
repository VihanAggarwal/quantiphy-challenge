import cv2, numpy as np, sys
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
def kasa(pts):
    x,y=pts[:,0].astype(float),pts[:,1].astype(float)
    A=np.c_[2*x,2*y,np.ones_like(x)]; b=x*x+y*y
    c=np.linalg.lstsq(A,b,rcond=None)[0]; r=np.sqrt(c[2]+c[0]**2+c[1]**2); return c[0],c[1],r
def edge_points(img,cx,cy,r0,angles,rmin=0.6,rmax=1.5):
    g=cv2.GaussianBlur(cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(float),(3,3),0)
    # use colour distance to background along rays: gradient magnitude of Lab
    lab=cv2.cvtColor(img,cv2.COLOR_BGR2LAB).astype(float)
    pts=[]
    for a in angles:
        rs=np.arange(rmin*r0,rmax*r0,0.25)
        xs=cx+rs*np.cos(a); ys=cy+rs*np.sin(a)
        prof=np.array([cv2.getRectSubPix(lab.astype(np.float32),(1,1),(float(x),float(y)))[0,0] for x,y in zip(xs,ys)])
        dprof=np.linalg.norm(np.diff(prof,axis=0),axis=1)
        j=np.argmax(dprof); pts.append((xs[j],ys[j]))
    return np.array(pts)
if __name__=='__main__':
    v=sys.argv[1]; k=int(sys.argv[2]); cx,cy,r0=map(float,sys.argv[3:6]); a0,a1=float(sys.argv[6]),float(sys.argv[7])
    fr=np.load(f'{S}/f0035{v}.npy')[k]
    ang=np.radians(np.arange(a0,a1,5))
    p=edge_points(fr,cx,cy,r0,ang)
    for it in range(3):
        X,Y,R=kasa(p); res=np.hypot(p[:,0]-X,p[:,1]-Y)-R
        keep=np.abs(res)<2.5*np.std(res)+0.5; p=p[keep]
    X,Y,R=kasa(p); res=np.hypot(p[:,0]-X,p[:,1]-Y)-R
    print(v,k,'centre (%.1f,%.1f) diameter %.2f px  n=%d rms %.2f'%(X,Y,2*R,len(p),np.sqrt((res**2).mean())))
