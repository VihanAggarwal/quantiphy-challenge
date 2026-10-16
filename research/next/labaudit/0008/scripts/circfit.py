# refined ball centre/radius per frame: colour mask, then fit circle to left/right/top boundary points (exclude bottom shadow)
import cv2, numpy as np, sys
v=sys.argv[1] if len(sys.argv)>1 else 'captured_0008'
F='/home/user/quantiphy-challenge/research/next/labaudit/0008/frames/'
out={}
for i in range(22,49):
    im=cv2.imread(f'{F}{v}_f{i:02d}.png')
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    m=((hsv[...,0]<=16)|(hsv[...,0]>=172))&(hsv[...,1]>140)&(hsv[...,2]>100)
    m=m.astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); mk=(lab==k).astype(np.uint8)
    cs,_=cv2.findContours(mk,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); c=max(cs,key=cv2.contourArea).reshape(-1,2).astype(float)
    # algebraic circle fit (Kasa) on upper 3/4 of contour
    ymin,ymax=c[:,1].min(),c[:,1].max()
    sel=c[c[:,1]<ymin+0.75*(ymax-ymin)]
    A=np.c_[2*sel[:,0],2*sel[:,1],np.ones(len(sel))]; b=(sel**2).sum(1)
    sol=np.linalg.lstsq(A,b,rcond=None)[0]; xc,yc=sol[:2]; r=np.sqrt(sol[2]+xc**2+yc**2)
    w=c[:,0].max()-c[:,0].min(); h=ymax-ymin
    out[i]=(xc,yc,r,w,h)
    print(f'{i:2d} t={i/24:.3f} fit c=({xc:.1f},{yc:.1f}) r={r:.1f}  bbox w={w:.0f} h={h:.0f}  x[{c[:,0].min():.0f},{c[:,0].max():.0f}] y[{ymin:.0f},{ymax:.0f}]')
np.save(f'/home/user/quantiphy-challenge/research/next/labaudit/0008/scripts/track_{v}.npy',np.array([[i,*out[i]] for i in sorted(out)]))
