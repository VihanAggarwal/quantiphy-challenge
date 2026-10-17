import cv2, numpy as np
from common import frames
v='simulation_0285'
fr=frames(v)
bg=np.median(np.stack([fr[i] for i in range(0,72,3)]),axis=0).astype(np.int16)
for i in [4,8,12,16,20,24,28,32,36,40,44,48,52,56]:
    d=np.abs(fr[i].astype(np.int16)-bg).max(axis=2)
    m=(d>25).astype(np.uint8)
    m[700:]=0  # exclude shadow region
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    ys,xs=np.nonzero(m)
    if len(xs)==0: continue
    # leftmost column per row band
    out=[]
    for (a,b) in [(405,440),(441,470)]:
        sel=(ys>=a)&(ys<=b)
        if sel.sum()==0: out.append(None); continue
        xm=xs[sel].min(); yy=ys[sel][xs[sel]==xm].mean()
        out.append((int(xm),round(float(yy),1)))
    print(i, 'bbox x',xs.min(),xs.max(),'y',ys.min(),ys.max(), 'tips',out)
