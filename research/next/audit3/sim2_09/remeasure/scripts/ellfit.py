import cv2, numpy as np, sys
vid=sys.argv[1]; trk=np.loadtxt(sys.argv[2],delimiter=',')
frames=[int(v) for v in sys.argv[3].split(',')]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
fr={}
i=0
while True:
    ok,f=c.read()
    if not ok: break
    if i in frames: fr[i]=f
    i+=1
ang=np.linspace(0,2*np.pi,720,endpoint=False); rad=np.arange(40,80,0.25)
for i in frames:
    img=cv2.GaussianBlur(fr[i].astype(np.float32),(0,0),1.0)
    cx,cy=trk[i,1],trk[i,2]
    X=(cx+np.cos(ang)[:,None]*rad[None,:]).astype(np.float32); Y=(cy+np.sin(ang)[:,None]*rad[None,:]).astype(np.float32)
    prof=cv2.remap(img,X,Y,cv2.INTER_LINEAR).sum(2)
    d=np.diff(prof,axis=1); j=np.argmin(d,axis=1)
    jj=np.clip(j,1,d.shape[1]-2); n=np.arange(len(ang))
    a,b,cc=d[n,jj-1],d[n,jj],d[n,jj+1]; den=a-2*b+cc
    off=np.where(np.abs(den)>1e-6,0.5*(a-cc)/np.where(np.abs(den)>1e-6,den,1),0)
    r=rad[0]+(jj+0.5+np.clip(off,-1,1))*0.25
    px=cx+np.cos(ang)*r; py=cy+np.sin(ang)*r
    # general conic fit -> ellipse
    pts=np.c_[px,py].astype(np.float32)
    keep=np.ones(len(px),bool)
    for _ in range(4):
        e=cv2.fitEllipse(pts[keep])
        (ex,ey),(w,h),th=e
        # residual approx
        rr=np.hypot(px-ex,py-ey); keep=np.abs(rr-np.median(rr[keep]))<4
    # extents along x and y from opposite rays
    def ext(a0):
        k0=int(round(a0/360*720))%720; k1=(k0+360)%720
        return r[k0]+r[k1]
    print(vid,i,'centre %.1f %.1f  ellipse axes %.2f %.2f th %.1f | x-extent %.2f y-extent %.2f diag45 %.2f diag135 %.2f'%(ex,ey,w,h,th,np.median([ext(a) for a in [-2,-1,0,1,2]]),np.median([ext(a) for a in [88,89,90,91,92]]),ext(45),ext(135)))
