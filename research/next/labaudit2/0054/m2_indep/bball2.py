from common import *
import numpy as np, cv2
fs=frames('ax'); fa=frames('a')
def fitcircle(p):
    A=np.c_[2*p[:,0],2*p[:,1],np.ones(len(p))]; bb=(p**2).sum(1)
    sol=np.linalg.lstsq(A,bb,rcond=None)[0]; cx,cy=sol[0],sol[1]; R=np.sqrt(sol[2]+cx**2+cy**2); return cx,cy,R
for i in list(range(0,5))+list(range(8,27)):
    f=fs[i]; b,g,r=[f[:,:,k].astype(int) for k in range(3)]
    bg=(g>180)&(r<120)&(b<120)
    fg=(~bg).astype(np.uint8); fg[690:,1020:]=0
    # seed at orange
    org=(r>g+30)&(r>b+40)&(r>90); org[690:,1020:]=False
    ys,xs=np.nonzero(org); 
    n,lab,st,cen=cv2.connectedComponentsWithStats(fg,8)
    ks=np.bincount(lab[ys,xs]); ks[0]=0; k=np.argmax(ks)
    m=(lab==k).astype(np.uint8)
    x,y,w,h,a=st[k]
    cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cnts,key=cv2.contourArea); p=c[:,0,:].astype(float); p=p[(p[:,1]<718)]
    cx,cy,R=fitcircle(p)
    print(i,'bbox',x,y,w,h,'area',a,'eqd',round(2*np.sqrt(a/np.pi),1),'circ',round(cx,1),round(cy,1),'D',round(2*R,1))
    if i in (13,24):
        crop=fa[i][int(cy-70):int(cy+70),int(cx-70):int(cx+70)].copy()
        crop=cv2.resize(crop,None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST)
        cv2.imwrite(OUT+'frames/bball_a_%d.png'%i,crop)
        crop=f[int(cy-70):int(cy+70),int(cx-70):int(cx+70)].copy()
        crop=cv2.resize(crop,None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST)
        cv2.imwrite(OUT+'frames/bball_ax_%d.png'%i,crop)
