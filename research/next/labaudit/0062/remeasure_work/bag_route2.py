import cv2, numpy as np
cx=640.;cy=360.;f=711.
n=np.load('n_fit_711.npy')[:3]
z=np.array([0,0,1.]); e2=z-(z@n)*n; e2/=np.linalg.norm(e2); e1=np.cross(n,e2)
def P2(uv):
    uv=np.atleast_2d(uv).astype(float); r=np.c_[(uv[:,0]-cx)/f,(uv[:,1]-cy)/f,np.ones(len(uv))]; X=r/(r@n)[:,None]; return np.c_[X@e1,X@e2]
hb=1.8212
# route 2a: manual visual corners
man=np.array([(771,315),(821,295.5),(895,347),(843,372)],float)
X=P2(man); s=[np.linalg.norm(X[(k+1)%4]-X[k]) for k in range(4)]
print('manual corners sides LT,TR,RB,BL cm',np.round(np.array(s)*hb*100,1))
# route 2b: SAM mask (x render median) with handle side cut by a manual line through T and R (slightly inside)
m=cv2.imread('bag_mask.png',0)>0
ys,xs=np.nonzero(m)
T=np.array([821,295.5]); R=np.array([895,347])
d=R-T; nrm=np.array([-d[1],d[0]]); nrm/=np.linalg.norm(nrm)   # points to which side?
side=(np.c_[xs,ys]-T)@nrm
body_sign=np.sign(((np.array([830,335])-T)@nrm))
keep=(side*body_sign)>=-1.0
pts=np.c_[xs,ys][keep].astype(float)
# use pixel corners for accuracy
offs=np.array([[0,0],[1,0],[0,1],[1,1]])-0.5
allp=(pts[:,None,:]+offs[None]).reshape(-1,2)
Q=P2(allp).astype(np.float32)
hull=cv2.convexHull(Q)
(rx,ry),(w,h),ang=cv2.minAreaRect(hull)
print('SAM-mask body minAreaRect (cm):',round(min(w,h)*hb*100,1),'x',round(max(w,h)*hb*100,1),'angle',round(ang,1))
# width profile: extent along side direction measured across the body (median over slices)
Xc=P2(np.load('bag_corners_trim.npy'))
uo=Xc[2]-Xc[1]; uo/=np.linalg.norm(uo); us=np.array([-uo[1],uo[0]])
a=(Q-Xc[0])@uo; b=(Q-Xc[0])@us
ext=[]
for t in np.linspace(a.min()+0.03,a.max()-0.03,15):
    sel=np.abs(a-t)<0.004
    if sel.sum()>5: ext.append(b[sel].max()-b[sel].min())
print('side-direction extent across slices (cm): median',round(np.median(ext)*hb*100,1),'range',round(min(ext)*hb*100,1),round(max(ext)*hb*100,1))
ext2=[]
for t in np.linspace(b.min()+0.03,b.max()-0.03,15):
    sel=np.abs(b-t)<0.004
    if sel.sum()>5: ext2.append(a[sel].max()-a[sel].min())
print('opening-direction extent across slices (cm): median',round(np.median(ext2)*hb*100,1))
