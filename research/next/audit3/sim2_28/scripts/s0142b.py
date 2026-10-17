import sys; sys.path.insert(0,'scripts')
from vid import frames
import cv2, numpy as np
F=frames('simulation_0142')
G=[f.astype(np.float32) for f in F]
bg=np.median(np.stack(G[::2]),axis=0)
out=[]
for i in range(len(G)):
    d=np.abs(G[i]-bg).max(axis=2); d[:380]=0; d[960:]=0
    m=(d>30)
    ys,xs=np.where(m)
    # head band: top 60 rows of mask
    top=np.percentile(ys,0.5)
    hb=(ys<top+60)
    torso=(ys>top+80)&(ys<top+250)
    out.append((i,xs.mean(),xs[hb].mean(),xs[torso].mean(),top,np.percentile(ys,99.5),len(xs)))
o=np.array(out)
for r in o[::10]: print(r.round(1))
for c,nm in [(1,'all'),(2,'head'),(3,'torso')]:
    sel=(o[:,0]>=3)&(o[:,0]<=76)
    p=np.polyfit(o[sel,0],o[sel,c],1); print(nm,p[0], 'resid std',np.std(o[sel,c]-np.polyval(p,o[sel,0])))
print('height px (top to bottom) median', np.median(o[:,5]-o[:,4]), 'min top',o[:,4].min())
