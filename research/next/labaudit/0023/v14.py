import cv2, numpy as np
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    from rest import onplane
h=0.170
prev=None
for pre in ['o','x']:
  prev=None
  for i in range(31,42):
    im=cv2.imread(f'frames/{pre}{i:02d}.png').astype(float); v=im.max(2)
    ys=[]
    for x in range(540,625,10):
        p=v[485:526,x-1:x+2].mean(1); k=np.argmin(p)
        if p[k]<110: ys.append(485+k)
    y=np.median(ys) if ys else np.nan
    P=onplane(580,y,h)
    sp='' if prev is None else '%.1f'%(np.linalg.norm(P-prev)*24*100)
    print(pre,i,'t=%.3f'%(i/24),'contact y %.1f (n=%d)'%(y,len(ys)),'z %.3f'%P[2],'step speed',sp)
    prev=P
