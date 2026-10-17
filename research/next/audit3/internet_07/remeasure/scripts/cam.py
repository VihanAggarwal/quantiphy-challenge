from load import load
import numpy as np, cv2
fr=load()
N=len(fr)
bg=np.median(np.stack(fr[96:114:2]),axis=0).astype(np.float32)
# cup rough x-range
box={}
for i in range(N):
    d=np.abs(fr[i].astype(np.float32)-bg)[680:980]
    col=(d>50).sum(0)
    xs=np.where(col>100)[0]
    if len(xs)>50: box[i]=(xs.min(),xs.max())
print({k:box[k] for k in sorted(box)})
res=[]
cum=np.zeros(2); cumA=np.eye(3)
for i in range(1,N):
    a,b=fr[i-1],fr[i]
    m=np.zeros_like(a); m[620:1080,:]=255; m[560:680,:]=255  # floor + baseboard
    m[:560]=0
    for j in (i-1,i):
        if j in box:
            x0,x1=box[j]; m[:, max(0,x0-450):min(1920,x1+350)]=0
    # exclude string band region near baseboard top when string present (rows 520-620) -> keep baseboard lower edge 600-680
    m[:600]=0
    p=cv2.goodFeaturesToTrack(a,800,0.01,8,mask=m,blockSize=7)
    if p is None or len(p)<10: res.append((i,np.nan,np.nan,0)); continue
    q,st,err=cv2.calcOpticalFlowPyrLK(a,b,p,None,winSize=(31,31),maxLevel=3)
    p2,st2,_=cv2.calcOpticalFlowPyrLK(b,a,q,None,winSize=(31,31),maxLevel=3)
    ok=(st[:,0]==1)&(st2[:,0]==1)&(np.linalg.norm(p2-p,axis=2)[:,0]<0.3)
    d=(q-p)[ok,0]
    A,inl=cv2.estimateAffinePartial2D(p[ok],q[ok],ransacReprojThreshold=0.5)
    res.append((i,np.median(d[:,0]),np.median(d[:,1]),ok.sum(),A[0,2],A[1,2],np.hypot(A[0,0],A[1,0])))
for r in res: print(' '.join(f'{v:.3f}' if isinstance(v,float) else str(v) for v in r))
