import cv2, numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from track import *
fr=frames('simulation_0022_segmented')
rows=[]
for i in range(0,62):
    m=fgmask(fr[i]); m[:,:565]=False
    hull=m.copy(); hull[:585]=False
    ys,xs=np.where(hull)
    if len(xs)==0: continue
    full = xs.max()<955
    rows.append((i,xs.min(),xs.max(),ys.min(),ys.max(),xs.mean(),ys.mean(),full))
for r in rows:
    if r[0]%4==0: print(r)
R=np.array([r for r in rows if r[7]],float)
t=R[:,0]
for k,name in [(5,'cx'),(6,'cy'),(1,'bow'),(2,'stern')]:
    c=np.polyfit(t,R[:,k],2); print(name,'fit at 24: %.2f at 48: %.2f'%(np.polyval(c,24),np.polyval(c,48)), 'resid %.2f'%np.std(R[:,k]-np.polyval(c,t)))
bows=np.array([[r[0],r[1]] for r in rows]); c=np.polyfit(bows[:,0],bows[:,1],2); print('bow (all frames) at 24 %.2f at 48 %.2f'%(np.polyval(c,24),np.polyval(c,48)))
