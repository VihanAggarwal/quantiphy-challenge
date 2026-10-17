import sys; sys.path.insert(0,'scripts')
from vid import frames
import cv2, numpy as np
F=frames('simulation_0162')
G=[f.astype(np.float32) for f in F]
bg=G[0]
out=[]
for i in range(1,len(G)):
    d=np.abs(G[i]-bg).max(axis=2)
    d[:500]=0; d[720:]=0
    # use blue chroma: ball is blue
    b,g,r=G[i][...,0],G[i][...,1],G[i][...,2]
    m=((d>40)&(b-r>15)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    if a<200: continue
    out.append((i,x,x+w,y,y+h,w,h,a,cen[k][0],cen[k][1]))
o=np.array(out,float)
for r in o[::6]: print(r.round(1))
np.savetxt('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/s0162.txt',o)
full=(o[:,1]>2)&(o[:,2]<1915)
print('w med',np.median(o[full,5]),'h med',np.median(o[full,6]),'eqd',2*np.sqrt(np.median(o[full,7])/np.pi))
