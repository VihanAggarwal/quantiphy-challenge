import numpy as np, cv2
from common import *
exec(open('wbplane.py').read().split('frames=[n')[0])
X=load('x')
mx=np.median(X[0:49:2].astype(float),0).astype(np.uint8)
M=(mx.max(2)>40).astype(np.uint8)
k,lab,st,cen=cv2.connectedComponentsWithStats(M,8)
def comp_at(u,v): return (lab==lab[v,u]).astype(np.uint8)
def floor_basis(nrm):
    a=np.array([1.0,0,0]); e1=a-(a@nrm)*nrm; e1/=np.linalg.norm(e1); e2=np.cross(nrm,e1); return e1,e2
def rect_on_plane(mask,nrm,delta,f=F,open_px=0):
    m=mask.copy()
    if open_px: m=cv2.morphologyEx(m,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(open_px,open_px)))
    k2,l2,s2,_=cv2.connectedComponentsWithStats(m,8); i=1+np.argmax(s2[1:,4]); m=(l2==i).astype(np.uint8)
    cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cs,key=cv2.contourArea).reshape(-1,2).astype(float)
    P=backproj(c,nrm,1.0-delta,f)
    e1,e2=floor_basis(nrm)
    q=np.c_[P@e1,P@e2].astype(np.float32)
    (cx,cy),(w,h),ang=cv2.minAreaRect(q)
    return max(w,h),min(w,h),m
for f,(p,r) in {700:(39.34,8.43),711:(38.93,8.53),722:(38.50,8.66)}.items():
    nrm=normal(p,r)
    bag=comp_at(837,329)
    for op in (0,7,9,11,13):
        L,W,_=rect_on_plane(bag,nrm,0.0,f,op)
        print(f,'bag open%d L/h=%.4f W/h=%.4f'%(op,L,W))
    # board at frame 48 as sanity (mask from frame)
    box=comp_at(517,495)
    for dl in (0.0,0.01,0.02,0.03):
        L,W,_=rect_on_plane(box,nrm,dl,f)
        print(f,'box delta%.2f L/h=%.4f W/h=%.4f'%(dl,L,W))
    mar=comp_at(635,624)
    for dl in (0.0,0.02,0.03,0.05):
        L,W,_=rect_on_plane(mar,nrm,dl,f)
        print(f,'mario delta%.2f L/h=%.4f W/h=%.4f'%(dl,L,W))
