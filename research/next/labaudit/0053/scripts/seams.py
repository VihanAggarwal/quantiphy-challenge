import cv2, numpy as np
med=cv2.imread('median_o.png').astype(float)
g=cv2.GaussianBlur(med.mean(2),(3,3),0)
seams={'A':((983,0),(900,220)),'B':((1133,0),(990,287)),'C':((1280,107),(1107,373)),'D':((880,0),(840,160))}
res={}
for k,(p0,p1) in seams.items():
    pts=[]
    for y in range(p0[1]+3,p1[1]-3,4):
        x0=p0[0]+(p1[0]-p0[0])*(y-p0[1])/(p1[1]-p0[1])
        xs=np.arange(int(x0)-8,int(x0)+9)
        xs=xs[(xs>=0)&(xs<1280)]
        prof=g[y,xs]
        i=np.argmin(prof); c=np.median(prof)-prof[i]
        if c>4 and 0<i<len(xs)-1:
            # subpixel parabola
            a,b,cc=prof[i-1],prof[i],prof[i+1]
            off=0.5*(a-cc)/(a-2*b+cc) if (a-2*b+cc)!=0 else 0
            pts.append((y,xs[i]+off))
    pts=np.array(pts)
    if len(pts)<5: print(k,'few',len(pts)); continue
    A=np.c_[np.ones(len(pts)),pts[:,0]]
    sol,*_=np.linalg.lstsq(A,pts[:,1],rcond=None)
    for it in range(2):
        r=pts[:,1]-A@sol; keep=np.abs(r)<1.5
        sol,*_=np.linalg.lstsq(A[keep],pts[keep,1],rcond=None)
    r=pts[keep,1]-A[keep]@sol
    res[k]=sol
    print(k,len(pts),keep.sum(),'x=%.1f + %.4f*y'%tuple(sol),'rms %.2f'%np.sqrt((r**2).mean()),'y',pts[keep,0].min(),pts[keep,0].max())
np.save('seams.npy',res)
# vertical VP: least squares intersection of lines x - b*y - a = 0
L=[]
for k,(a,b) in res.items(): L.append([1,-b,-a])
L=np.array(L,float); L/=np.linalg.norm(L[:,:2],axis=1)[:,None]
A=L[:,:2]; c=-L[:,2]
vp,*_=np.linalg.lstsq(A,c,rcond=None)
print('VP',vp)
for i,k1 in enumerate(res):
    for k2 in list(res)[i+1:]:
        a1,b1=res[k1];a2,b2=res[k2]
        y=(a2-a1)/(b1-b2); print(k1,k2,'VP pair',round(a1+b1*y,1),round(y,1))
