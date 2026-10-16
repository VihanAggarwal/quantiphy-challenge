import cv2, numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0035/remeasure_work')
from ballfit import blob, edge_fit
W='/home/user/quantiphy-challenge/research/next/labaudit/0035/remeasure_work/'
v=sys.argv[1]
F=np.load(W+v+'.npy')
cx,cy=640,360
near=(830,280)
res=[]
def width_along(f, c, n, r0, chan='sat', band=4, mode='grad'):
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV).astype(np.float32)
    g=hsv[...,1] if chan=='sat' else (f[...,2].astype(np.float32)-f[...,0].astype(np.float32))
    g=cv2.GaussianBlur(g,(3,3),0)
    n=np.array(n)/np.linalg.norm(n); p=np.array([-n[1],n[0]])
    ts=np.arange(-1.7*r0,1.7*r0,0.2)
    prof=[]
    for o in np.arange(-band,band+0.1,1.0):
        xs=c[0]+ts*n[0]+o*p[0]; ys=c[1]+ts*n[1]+o*p[1]
        prof.append(cv2.remap(g,xs.astype(np.float32).reshape(1,-1),ys.astype(np.float32).reshape(1,-1),cv2.INTER_LINEAR)[0])
    prof=np.mean(prof,0)
    mid=len(ts)//2
    inside=np.median(prof[np.abs(ts)<0.5*r0])
    outside=0.5*(np.median(prof[ts<-1.35*r0])+np.median(prof[ts>1.35*r0]))
    if mode=='grad':
        d=np.gradient(prof)
        a=np.argmax(d[:mid]); b=mid+np.argmin(d[mid:])
        return ts[b]-ts[a]
    else:
        thr=0.5*(inside+outside)
        # left crossing: last index left of centre below thr
        L=np.where(prof[:mid]<thr)[0]; Rr=np.where(prof[mid:]<thr)[0]
        a=L[-1]; b=mid+Rr[0]
        # subpixel interpolate
        xa=ts[a]+(thr-prof[a])/(prof[a+1]-prof[a])*0.2
        xb=ts[b-1]+(thr-prof[b-1])/(prof[b]-prof[b-1])*0.2
        return xb-xa
cent=[]
for i in range(len(F)):
    m,c,st=blob(F[i],near)
    r0=np.sqrt(st[4]/np.pi)
    P=edge_fit(F[i],c,r0)
    rr=np.hypot(P[:,0]-c[0],P[:,1]-c[1]); keep=(np.abs(rr-np.median(rr))<0.25*np.median(rr))
    (ex,ey),_,_=cv2.fitEllipse(P[keep,:2].astype(np.float32))
    cent.append((ex,ey)); near=(int(ex),int(ey))
cent=np.array(cent)
for i in range(len(F)):
    c=cent[i]
    mv=cent[min(i+1,len(F)-1)]-cent[max(i-1,0)]
    if np.linalg.norm(mv)<3: mv=np.array([1.,0.])
    perp=np.array([-mv[1],mv[0]])
    rad=c-np.array([cx,cy]); tang=np.array([-rad[1],rad[0]])
    r0=30
    out=[]
    for n in [perp,mv,tang,rad]:
        out.append(width_along(F[i],c,n,r0,'sat',4,'grad'))
        out.append(width_along(F[i],c,n,r0,'sat',4,'half'))
        out.append(width_along(F[i],c,n,r0,'rb',4,'half'))
    print(i,'c=(%.1f,%.1f)'%tuple(c),'perp g/h/rb=%.1f %.1f %.1f | along=%.1f %.1f %.1f | tang=%.1f %.1f %.1f | rad=%.1f %.1f %.1f'%tuple(out), 'mvdir=%.0f'%np.degrees(np.arctan2(mv[1],mv[0])), 'raddir=%.0f'%np.degrees(np.arctan2(rad[1],rad[0])))
np.save(W+v+'_cent.npy',cent)
