from common import *
import numpy as np, cv2
fs=frames('ax')
for i in range(0,34):
    f=fs[i]; b,g,r=[f[:,:,k].astype(int) for k in range(3)]
    org=(r>g+30)&(r>b+40)&(r>90)
    org[690:,1020:]=False
    n,lab,st,cen=cv2.connectedComponentsWithStats(org.astype(np.uint8),8)
    if n<2: print(i,'none'); continue
    k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
    m=(lab==k).astype(np.uint8)
    cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cnts,key=cv2.contourArea)
    (ex,ey),rad=cv2.minEnclosingCircle(c)
    # fit circle to contour points not on image border
    p=c[:,0,:].astype(float); p=p[(p[:,1]<718)&(p[:,1]>1)]
    A=np.c_[2*p[:,0],2*p[:,1],np.ones(len(p))]; bb=(p**2).sum(1)
    sol=np.linalg.lstsq(A,bb,rcond=None)[0]; cx,cy=sol[0],sol[1]; R=np.sqrt(sol[2]+cx**2+cy**2)
    print(i,'bbox',x,y,w,h,'area',a,'eqd',round(2*np.sqrt(a/np.pi),1),'fitc',round(cx,1),round(cy,1),'D',round(2*R,1))
