import cv2, numpy as np
base='/home/user/quantiphy-challenge/research/next/labaudit/0001/'
f=711.; cx=640.; cy=360.
def fit(i):
    im=cv2.imread(base+'frames/f%02d.png'%i)
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    m=((hsv[...,0]>18)&(hsv[...,0]<42)&(hsv[...,1]>80)&(hsv[...,2]>100)).astype(np.uint8)
    m[690:,1000:]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m); k=1+np.argmax(st[1:,4])
    B=(lab==k).astype(np.uint8)
    cnts,_=cv2.findContours(B,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cnts,key=len)[:,0,:].astype(float)
    # algebraic circle fit on upper 2/3 of contour (exclude bottom contact)
    yc=c[:,1].mean()
    sel=c[c[:,1]<yc+0.3*(c[:,1].max()-c[:,1].min())]
    A=np.c_[2*sel[:,0],2*sel[:,1],np.ones(len(sel))]; b=(sel**2).sum(1)
    x0,y0,cc=np.linalg.lstsq(A,b,rcond=None)[0]; R=np.sqrt(cc+x0**2+y0**2)
    (ex,ey),er=cv2.minEnclosingCircle(c.astype(np.float32))
    return x0,y0,R,er,B.sum()
for i in [0,5,10,20,27,38]:
    x0,y0,R,er,a=fit(i)
    print(i,'circle centre (%.1f,%.1f) R=%.2f px  minEncl R=%.2f  area-eq R=%.2f'%(x0,y0,R,er,np.sqrt(a/np.pi)))
x0,y0,R,er,a=fit(0)
for name,rng in [('label as centre',1.1075),('label as front +r',1.1075+0.0335)]:
    d=np.hypot(x0-cx,y0-cy); th=np.arctan(d/f)
    ang=np.arctan((d+R)/f)-np.arctan((d-R)/f)
    print(name,'D=%.2f cm'%(200*rng*np.sin(ang/2)))
