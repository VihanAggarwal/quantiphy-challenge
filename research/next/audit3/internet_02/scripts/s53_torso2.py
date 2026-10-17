import cv2, numpy as np
P='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0053.mp4'
c=cv2.VideoCapture(P); G=[]
while True:
    ok,im=c.read()
    if not ok: break
    G.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32))
N=len(G)
def track(tf, box, x_init):
    x0,y0,w,h=box; T=G[tf][y0:y0+h,x0:x0+w].copy()
    xs=np.full(N,np.nan); scs=np.zeros(N); prev=x_init
    for i in range(N):
        band=G[i][y0-30:y0+h+30]
        r=cv2.matchTemplate(band,T,cv2.TM_CCOEFF_NORMED)
        m=np.full(r.shape,-1,np.float32); a0=int(max(0,prev-10)); a1=int(min(r.shape[1],prev+45)); m[:,a0:a1]=r[:,a0:a1]
        _,mx,_,ml=cv2.minMaxLoc(m); x,y=ml
        dx=0
        if 0<x<r.shape[1]-1:
            a,b,cc=r[y,x-1],r[y,x],r[y,x+1]; den=a-2*b+cc; dx=0.5*(a-cc)/den if den!=0 else 0
        xs[i]=x+dx; scs[i]=mx; prev=x+18
    return xs,scs
xa,sa=track(40,(1170,385,90,135),390)
xb,sb=track(40,(1150,640,210,75),360)   # scooter deck + wheels + shoes
for i in range(0,N,5): print(i, round(xa[i],1), round(sa[i],2), round(xb[i],1), round(sb[i],2))
t=np.arange(N)
for nm,x,s in (('torso',xa,sa),('scooter',xb,sb)):
    ok=s>0.55
    p=np.polyfit(t[ok],x[ok],2)
    print(nm,'valid',t[ok].min(),t[ok].max(),'n',ok.sum(),'quad v at 0,40,80',np.round(np.polyval(np.polyder(p),[0,40,80]),2),
          'mean v (endpoints of valid)',round((x[t[ok].max()]-x[t[ok].min()])/(t[ok].max()-t[ok].min()),2),
          'fit avg v 0..80', round((np.polyval(p,80)-np.polyval(p,0))/80,2))
np.savez('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/i02/rider.npz',xa=xa,sa=sa,xb=xb,sb=sb)
