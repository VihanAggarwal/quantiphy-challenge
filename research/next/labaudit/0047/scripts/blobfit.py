import cv2, numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0047/scripts')
from track import *
def fit_blob(path, roi, f_px=F, band=0.12, ybot=703, show=None):
    f=cv2.imread(path).astype(int)
    green=(f[:,:,1]>150)&(f[:,:,0]<110)&(f[:,:,2]<110)
    fg=(~green).astype(np.uint8)
    x0,y0,x1,y1=roi
    m=np.zeros_like(fg); m[y0:y1,x0:x1]=fg[y0:y1,x0:x1]
    # largest component in roi
    nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,cv2.CC_STAT_AREA]); m=(lab==k).astype(np.uint8)
    dt=cv2.distanceTransform(m,cv2.DIST_L2,5)
    yy,xx=np.unravel_index(np.argmax(dt),dt.shape); r=dt[yy,xx]; cx,cy=float(xx),float(yy)
    er=cv2.erode(m,np.ones((3,3),np.uint8))
    bd=(m==1)&(er==0)
    # boundary must be adjacent to green (not to other fg)
    gd=cv2.dilate(green.astype(np.uint8),np.ones((3,3),np.uint8))
    bd&=gd.astype(bool)
    bd[ybot:]=False
    ys,xs=np.nonzero(bd); pts=np.stack([xs,ys],1).astype(float)
    for it in range(8):
        dd=np.hypot(pts[:,0]-cx,pts[:,1]-cy)
        sel=(dd>r-3)&(dd<r*1.35) if it==0 else np.abs(dd-r)<max(4,band*r)
        P=pts[sel]
        A=np.c_[2*P[:,0],2*P[:,1],np.ones(len(P))]; b=(P**2).sum(1)
        s=np.linalg.lstsq(A,b,rcond=None)[0]; cx,cy=s[0],s[1]; r=np.sqrt(s[2]+cx**2+cy**2)
    dd=np.hypot(pts[:,0]-cx,pts[:,1]-cy); P=pts[np.abs(dd-r)<max(4,band*r)]
    c,a,rr,w=fit_cone(P,rays(np.array([cx]),np.array([cy]),f_px)[0],np.arctan(r/f_px),f_px)
    pc=proj(c,f_px)
    if show is not None:
        img=cv2.imread(path.replace('x_','o_') if False else path)
        e1=np.cross(c,[0,1,0]); e1/=np.linalg.norm(e1); e2=np.cross(c,e1)
        th=np.linspace(0,2*np.pi,200)
        d=np.cos(a)*c[None]+np.sin(a)*(np.cos(th)[:,None]*e1+np.sin(th)[:,None]*e2)
        p=np.stack([CX+f_px*d[:,0]/d[:,2],CY+f_px*d[:,1]/d[:,2]],1).astype(np.int32)
        cv2.polylines(img,[p],True,(0,0,255),1)
        for q in P[w>0].astype(int): img[q[1],q[0]]=(255,0,255)
        X0=max(0,int(cx-r*1.6)); Y0=max(0,int(cy-r*1.6)); X1=int(cx+r*1.6); Y1=int(cy+r*1.6)
        crop=img[Y0:Y1,X0:X1]; s=300/max(crop.shape[:2]); cv2.imwrite(show,cv2.resize(crop,None,fx=s,fy=s,interpolation=cv2.INTER_NEAREST))
    return dict(circ=(cx,cy,r),pc=pc,alpha=a,sin=np.sin(a),c=c,n=len(P),inl=int(w.sum()),rms=float(np.sqrt(np.mean(rr[w>0]**2))*f_px))
