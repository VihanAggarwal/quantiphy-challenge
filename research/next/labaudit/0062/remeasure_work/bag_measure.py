import cv2, numpy as np
f=711.;cx=640.;cy=360.
n=np.load('n_fit_711.npy')[:3]
z=np.array([0,0,1.]); e2=z-(z@n)*n; e2/=np.linalg.norm(e2); e1=np.cross(n,e2)
m=cv2.imread('bag_mask.png',0)>0
# contour in image -> plane coords (units of h)
def to_plane(uv):
    r=np.c_[(uv[:,0]-cx)/f,(uv[:,1]-cy)/f,np.ones(len(uv))]; X=r/(r@n)[:,None]
    return np.c_[X@e1,X@e2]
# rasterize mask into plane at high res: map each mask pixel corner
ys,xs=np.nonzero(m)
P=to_plane(np.c_[xs,ys].astype(float))
res=0.001  # 1 mm in h-units (~0.18cm)
mn=P.min(0)-0.02
# better: inverse-map grid
N=int((P.max(0)-mn).max()/res)+40
a=mn[0]+np.arange(N)*res; b=mn[1]+np.arange(N)*res
A,B=np.meshgrid(a,b)
X=A[...,None]*e1+B[...,None]*e2
# X lies in plane through origin; need plane n.X=1: add n
X=X+n[None,None,:]*1.0
u=f*X[...,0]/X[...,2]+cx; v=f*X[...,1]/X[...,2]+cy
top=cv2.remap(m.astype(np.float32),u.astype(np.float32),v.astype(np.float32),cv2.INTER_LINEAR)>0.5
top=top.astype(np.uint8)
cv2.imwrite('bag_top_mask_hunits.png',top*255)
for k in [0,9,15,21,27]:
    t=top if k==0 else cv2.morphologyEx(top,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k)))
    nl,lab,st,cen=cv2.connectedComponentsWithStats(t); j=1+np.argmax(st[1:,4]); t=(lab==j).astype(np.uint8)
    cnts,_=cv2.findContours(t,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); c=max(cnts,key=cv2.contourArea)
    (rx,ry),(w,hh),ang=cv2.minAreaRect(c)
    area=t.sum()*res*res
    print('open',k,'minAreaRect sides (h units)',round(w*res,4),round(hh*res,4),'ang',round(ang,1),'area',round(area,4),'fill',round(area/(w*hh*res*res),3))
    if k==21: cv2.imwrite('bag_top_open21.png',t*255)
