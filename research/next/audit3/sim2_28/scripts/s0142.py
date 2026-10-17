import sys; sys.path.insert(0,'scripts')
from vid import frames
import cv2, numpy as np
F=frames('simulation_0142')
G=[f.astype(np.float32) for f in F]
bg=np.median(np.stack(G[::2]),axis=0)
out=[]
for i in range(len(G)):
    d=np.abs(G[i]-bg).max(axis=2); d[:350]=0; d[950:]=0
    m=(d>40).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    k=1+np.argmax(st[1:,4])
    ys,xs=np.where(lab==k)
    top=ys.min()
    out.append((i,cen[k][0],xs[ys<top+40].mean(),top,ys.max(),st[k][4]))
o=np.array(out)
for r in o[::8]: print(r.round(1))
sel=(o[:,5]>5000)
print('n',sel.sum(),'centroid slope',np.polyfit(o[sel,0],o[sel,1],1)[0],'head slope',np.polyfit(o[sel,0],o[sel,2],1)[0])
# full-clip motion? check centroid at first/last
print('x first/last',o[0,1],o[-1,1])
# tile grout: row profile near y=905 of background, find dark lines
row=cv2.cvtColor(bg.astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(float)
for y in [880,905,930]:
    p=row[y-2:y+3].mean(axis=0)
    p=p-cv2.GaussianBlur(p.reshape(1,-1),(1,41),0).ravel()
    idx=[x for x in range(130,1790) if p[x]<-6 and p[x]==p[x-6:x+7].min()]
    print(y, idx, np.diff(idx))
