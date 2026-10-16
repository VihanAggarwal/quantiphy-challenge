import cv2, numpy as np, sys
sys.path.insert(0,'scripts')
from xmask import xmask
F=711.;CX=640.;CY=360.
def rays(p,f=F):
    d=np.c_[(p[:,0]-CX)/f,(p[:,1]-CY)/f,np.ones(len(p))]; return d/np.linalg.norm(d,axis=1)[:,None]
def conefit(pts,f=F):
    r=rays(pts,f)
    keep=np.ones(len(r),bool)
    for it in range(4):
        w,*_=np.linalg.lstsq(r[keep],np.ones(keep.sum()),rcond=None)
        c=w/np.linalg.norm(w); a=np.arccos(1/np.linalg.norm(w))
        res=np.arccos(np.clip(r@c,-1,1))-a
        sc=max(1.5/f,2.5*np.median(np.abs(res[keep])))
        keep=np.abs(res)<sc
    uc=CX+f*c[0]/c[2]; vc=CY+f*c[1]/c[2]
    return uc,vc,a,np.abs(res[keep]).mean()*f
def boundary(m, box):
    x0,y0,x1,y1=box
    sub=np.zeros_like(m); sub[y0:y1,x0:x1]=m[y0:y1,x0:x1]
    cs,_=cv2.findContours(sub,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cs,key=cv2.contourArea)[:,0,:].astype(float)
    return c
if __name__=='__main__':
    for n,box,sel in [(0,(540,430,700,600),'f0'),(24,(490,440,660,630),'f24')]:
        m=xmask(n)
        c=boundary(m,box)
        # rough centre
        if n==0: uc,vc=612,508
        else: uc,vc=572,544
        ang=np.degrees(np.arctan2(c[:,1]-vc,c[:,0]-uc))  # 0=right, 90=down
        # exclude box-border points
        inb=(c[:,0]>box[0]+1)&(c[:,0]<box[2]-2)&(c[:,1]>box[1]+1)&(c[:,1]<box[3]-2)
        for nm,keep in ({'f0':{'left+bottom (95..215 deg & 30..95)':((ang>95)&(ang<215))|((ang>30)&(ang<=95)),
                                'left only 135..215':(ang>135)&(ang<215),
                                'left+lowerleft 100..215':(ang>100)&(ang<215)},
                         'f24':{'left+right sides':((ang>150)|(ang<-150))|((ang>-30)&(ang<30)),
                                'left 120..240':(ang>120)|(ang<-120),
                                'all but top-right':~((ang<-10)&(ang>-100))}}[sel]).items():
            k=keep&inb
            uc2,vc2,a,rms=conefit(c[k])
            print(n,nm,'npts',k.sum(),'centre (%.1f,%.1f) alpha=%.5f (2fa=%.1f px) rms=%.2f px'%(uc2,vc2,a,2*F*np.tan(a),rms))
