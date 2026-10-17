import sys; sys.path.insert(0,'scripts')
from vid import frames
import cv2, numpy as np
F=frames('simulation_0132')
G=[f.astype(np.float32) for f in F]
bg=np.median(np.stack(G[100:300:4]),axis=0)
out=[]
for i in range(130,200):
    d=np.abs(G[i]-bg).max(axis=2)
    d[:1000]=0; d[:,600:]=0; d[1850:]=0
    m=(d>30).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    k=1+np.argmax(st[1:,4])
    x,y,w,hh,a=st[k]
    out.append((i,cen[k][0],cen[k][1],w,hh,a,y,x))
o=np.array(out)
for r in o[::6]: print(r.round(1))
sel=(o[:,0]>=150)&(o[:,0]<=188)
p=np.polyfit(o[sel,0],o[sel,2],2); a=2*p[0]*120*120
px=np.polyfit(o[sel,0],o[sel,1],1)
s=9.8/a
print('a',a,'scale',s,'vx px/s',px[0]*120,'vx m/s',px[0]*120*s, 'vertex frame', -p[1]/(2*p[0]), 'vertex y', np.polyval(p,-p[1]/(2*p[0])))
print('diam px median w,h',np.median(o[sel,3]),np.median(o[sel,4]), 'eq', 2*np.sqrt(np.median(o[sel,5])/np.pi), 'm', np.median(o[sel,3])*s)
