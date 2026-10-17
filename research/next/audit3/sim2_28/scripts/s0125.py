import sys; sys.path.insert(0,'scripts')
from vid import frames
import cv2, numpy as np
F=[f.astype(np.float32) for f in frames('simulation_0125')]
# background: frame 70 for left half, frame 1 for right half
bg=F[70].copy(); bg[:,540:]=F[1][:,540:]
out=[]
for i in range(1,71):
    d=np.abs(F[i]-bg).max(axis=2)
    d[:600]=0; d[880:]=0
    m=(d>25).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    # head x: mean x of top 20 rows of component
    ys,xs=np.where(lab==k)
    top=ys.min()
    hx=xs[ys<top+20].mean()
    out.append((i,x,y,w,h,a,cen[k][0],hx,ys.max()))
o=np.array(out,float)
for r in o[::5]: print(r.round(1))
sel=(o[:,5]>2000)
print('n',sel.sum())
print('centroid slope',np.polyfit(o[sel,0],o[sel,6],1)[0],'head slope',np.polyfit(o[sel,0],o[sel,7],1)[0])
print('heights', np.percentile(o[sel,8]-o[sel,2]+1,[50,90,100]))
