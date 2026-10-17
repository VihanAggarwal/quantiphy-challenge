import sys; sys.path.insert(0,'scripts')
from vid import frames
import cv2, numpy as np
F=frames('simulation_0137')
G=[f.astype(np.float32) for f in F]
bg=np.median(np.stack(G[::3]),axis=0)
out=[]
for i in range(len(G)):
    d=np.abs(G[i]-bg).max(axis=2); d[880:]=0
    m=(d>30).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    k=1+np.argmax(st[1:,4])
    if st[k][4]<30: continue
    out.append((i,cen[k][0],cen[k][1],st[k][2],st[k][3],st[k][4]))
o=np.array(out)
for r in o[::10]: print(r.round(1))
v=np.hypot(np.diff(o[:,1]),np.diff(o[:,2]))/np.diff(o[:,0])
print('median px/frame',np.median(v), 'n',len(o), 'first',o[0,0],'last',o[-1,0])
# path length in px along smoothed track
from numpy.polynomial import polynomial as P
t=o[:,0]
px=np.polyfit(t,o[:,1],5); py=np.polyfit(t,o[:,2],5)
tt=np.linspace(t[0],t[-1],2000)
L=np.sum(np.hypot(np.diff(np.polyval(px,tt)),np.diff(np.polyval(py,tt))))
print('path px',L,'per frame',L/(t[-1]-t[0]))
print('frame60',o[o[:,0]==60])
cv2.imwrite('s0137_f60.png', cv2.resize(F[60],(960,540)))
