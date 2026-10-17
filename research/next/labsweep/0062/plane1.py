import numpy as np
from geo import *
pts={'wb':(705.4,415.3,2.815),'bag':(837.4,329.1,3.307),'box':(516.8,495.4,2.082),'trash':(337.8,156.8,2.303),'mario':(635,623.8,2.016)}
P={k:bp(*v) for k,v in pts.items()}
for k,p in P.items(): print(k,p.round(3))
A=np.array([P[k] for k in ['wb','bag','box','mario']])
c=A.mean(0); u,s,vt=np.linalg.svd(A-c); n=vt[2]; 
if n[1]>0: n=-n
print('normal',n.round(3),'resid',((A-c)@n).round(3))
d=-n@c; print('camera height above plane',d)
print('tilt deg', np.degrees(np.arccos(abs(n[1]))))
