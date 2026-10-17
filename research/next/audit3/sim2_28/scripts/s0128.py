import sys; sys.path.insert(0,'scripts')
from vid import frames
import cv2, numpy as np
for v in ['simulation_0128_segmented','simulation_0128']:
    F=[f.astype(np.float32) for f in frames(v)]
    out=[]
    for i,f in enumerate(F):
        b,g,r=f[...,0],f[...,1],f[...,2]
        red=(r-np.maximum(g,b))
        sub=red[:, 850:1080]
        m=sub>60
        ys,xs=np.where(m)
        if len(ys)<20: continue
        w=np.clip(sub[m]/ np.percentile(sub[m],90),0,1)
        cy=(ys*w).sum()/w.sum()
        out.append((i,cy,ys.max()-ys.min()+1,xs.max()-xs.min()+1, w.sum()))
    o=np.array(out)
    sel=o[:,0]>=2
    p=np.polyfit(o[sel,0],o[sel,1],2); a=2*p[0]*576
    eqd=2*np.sqrt(np.median(o[:,4])/np.pi)
    print(v,'a',a,'scale',9.8/a,'vertex',-p[1]/(2*p[0]),'h,w med',np.median(o[:,2]),np.median(o[:,3]),'eqdiam',eqd, 'D m',eqd*9.8/a)
