# vertical half-contrast extent of W and G near the apex in camera a (motion there is nearly horizontal, so vertical extent ~ diameter)
import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure')
import cv2,numpy as np
from pts import aW,aG
D='/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure/frames'
for v in ['a','as']:
  for k in [25,26,27,28,29]:
    img=cv2.imread(f'{D}/{v}_{k:02d}.png').astype(float)
    out=[]
    for nm,tr in [('W',aW),('G',aG)]:
        cx,cy=tr[k]; cx=int(round(cx)); cy=int(round(cy))
        win=img[cy-16:cy+17, cx-3:cx+4]   # 7 central columns
        prof=win.mean(1)                   # (33,3)
        bg=np.r_[prof[:4],prof[-4:]].mean(0)
        dist=np.linalg.norm(prof-bg,axis=1)
        pk=np.sort(dist)[-3:].mean(); thr=pk/2
        ins=np.where(dist>thr)[0]; i0,i1=ins[0],ins[-1]
        lo=i0-1+(thr-dist[i0-1])/(dist[i0]-dist[i0-1]); hi=i1+(dist[i1]-thr)/(dist[i1]-dist[i1+1])
        out.append((nm,hi-lo))
    print(v,k,' '.join(f'{n} vext={w:.1f}px' for n,w in out),' W/G=%.3f'%(out[0][1]/out[1][1]))
