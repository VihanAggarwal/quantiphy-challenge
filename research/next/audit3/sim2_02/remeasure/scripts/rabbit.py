import sys; sys.path.insert(0,'scripts')
from load import frames
import numpy as np, cv2
Y0=980
F=frames('simulation_0240',Y0,1100)[:49].astype(np.int16)
bg=np.median(F,axis=0)
res=[]
for k in range(49):
    xc=int(610+6.05*k)
    x0=max(0,xc-70); x1=min(1080,xc+70)
    f=F[k,:,x0:x1]; b=bg[:,x0:x1]
    D=np.abs(f-b).sum(axis=2)
    B,G,R=f[...,0],f[...,1],f[...,2]
    tan=(R-G>18)&(R>110)
    m=((D>45)&tan).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    # biggest component
    i=1+np.argmax(st[1:,4])
    # union of comps near biggest
    bx,by,bw,bh,ba=st[i]
    keep=np.zeros_like(m)
    for j in range(1,n):
        x,y,w,h,a=st[j]
        if a>=4 and x<bx+bw+6 and x+w>bx-6 and y<by+bh+6 and y+h>by-6:
            keep|=(lab==j).astype(np.uint8)
    ys,xs=np.nonzero(keep)
    cols=keep.sum(axis=0)
    xs_on=np.nonzero(cols>=2)[0]
    res.append((k,x0+xs.min(),x0+xs.max(),x0+xs_on.min(),x0+xs_on.max(),Y0+ys.min(),Y0+ys.max(),x0+xs.mean(),Y0+ys.mean(),keep.sum()))
res=np.array(res)
np.set_printoptions(suppress=True,precision=1,linewidth=150)
print('k xmin xmax xmin2 xmax2 ymin ymax cx cy area')
print(res)
L=res[:,2]-res[:,1]+1; L2=res[:,4]-res[:,3]+1
print('len all', np.median(L), L.mean(), ' len cols>=2', np.median(L2), L2.mean())
p=np.polyfit(res[:,0],res[:,7],1); print('cx slope',p)
p=np.polyfit(res[:,0],res[:,2],1); print('xmax slope',p)
p=np.polyfit(res[:,0],res[:,1],1); print('xmin slope',p)
print('ymax median',np.median(res[:,6]))
