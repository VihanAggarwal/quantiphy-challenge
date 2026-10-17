from common import *
import json
res={}
for k in range(18,49):
    im=frames('bx')[k].astype(np.int32)
    m=(im.sum(2)>45).astype(np.uint8); reg=np.zeros_like(m); reg[300:700,780:1000]=1; m=m*reg
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    i=1+np.argmax(st[1:,4]); ys,xs=np.nonzero(lab==i)
    pts=np.stack([xs,ys],1).astype(np.float32); hull=cv2.convexHull(pts)
    (ex,ey),(ea,eb),ang=cv2.fitEllipse(hull)
    A=st[i,4]; deq=2*np.sqrt(A/np.pi)
    res[k]=dict(c=(float(ex),float(ey)),m=(float(xs.mean()),float(ys.mean())),ea=float(max(ea,eb)),eb=float(min(ea,eb)),deq=float(deq),w=int(st[i,2]),h=int(st[i,3]))
    print(k,cap(k),'ell=(%.1f,%.1f) %.1fx%.1f deq=%.1f w=%d h=%d'%(ex,ey,max(ea,eb),min(ea,eb),deq,st[i,2],st[i,3]))
json.dump(res,open(OUT+'/soccer_b.json','w'))
