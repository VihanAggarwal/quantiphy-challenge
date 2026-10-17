import cv2,numpy as np
def frames(v,crop=None):
    cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4'); F=[]
    while True:
        ok,f=cap.read()
        if not ok: break
        F.append(f if crop is None else f[crop[0]:crop[1],crop[2]:crop[3]].copy())
    return F
# FRONT 0231
F=frames('simulation_0231',(550,800,0,1100))
front=[]
for i,f in enumerate(F):
    dark=(f.astype(int).sum(2)<150).astype(np.uint8)
    dark=cv2.morphologyEx(dark,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(dark)
    k=1+np.argmax(st[1:,4]); m=lab==k
    ys,xs=np.nonzero(m)
    # body band: rows where row-width >= 60% of max row width
    rw=m.sum(1); band=np.nonzero(rw>=0.6*rw.max())[0]
    bm=m.copy(); bm[:band.min()]=0; bm[band.max()+1:]=0
    yb,xb=np.nonzero(bm)
    front.append((i,xs.min(),xs.max(),xb.min(),xb.max(),xs.mean(),xb.mean(),band.min()+550,band.max()+550))
front=np.array(front,float)
# TOP segmented
F=frames('simulation_0233_segmented')
top=[]
for i,f in enumerate(F):
    m=(f.astype(int).sum(2)<300); m[:,1400:]=0
    m=m.astype(np.uint8); n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); m=lab==k
    ys,xs=np.nonzero(m)
    th=m.sum(0); body=np.nonzero(th>=0.6*th.max())[0]
    bm=m.copy(); bm[:,:body.min()]=0; bm[:,body.max()+1:]=0
    yb,xb=np.nonzero(bm)
    top.append((i,xs.min(),xs.max(),body.min(),body.max(),xs.mean(),xb.mean(),th.max(),0))
top=np.array(top,float)
s=np.arange(14,50)
for nm,A in [('front',front),('top',top)]:
    for c,lab in [(2,'nose'),(4,'bodyR'),(3,'bodyL'),(6,'bodycx'),(1,'tail')]:
        p=np.polyfit(A[s,0],A[s,c],1); print(nm,lab,'%.3f'%p[0])
vf=np.polyfit(front[s,0],front[s,6],1)[0]; vt=np.polyfit(top[s,0],top[s,6],1)[0]
print('frame front: tail..nose  body(L..R)  | top: tail..nose body  (in frames of travel, front v=%.3f top v=%.3f)'%(vf,vt))
for i in s:
    a=front[i]; b=top[i]
    print(int(i),'F %5.1f %5.1f'%((a[2]-a[1])/vf,(a[4]-a[3])/vf),' T %5.1f %5.1f'%((b[2]-b[1])/vt,(b[4]-b[3])/vt), ' Fpx',a[2]-a[1],a[4]-a[3],' Tpx',b[2]-b[1],b[4]-b[3])
F2=front[s]; T2=top[s]
print('mean F tail-nose %.2f body %.2f ; T tail-nose %.2f body %.2f'%(np.mean((F2[:,2]-F2[:,1])/vf),np.mean((F2[:,4]-F2[:,3])/vf),np.mean((T2[:,2]-T2[:,1])/vt),np.mean((T2[:,4]-T2[:,3])/vt)))
