# Tail tip in glide frames from the silhouette: extreme mask point along the tail direction; fit t*
import cv2, numpy as np
bg=np.load('bg0302.npy').astype(np.float32)
d=np.load('joint0302.npz'); vp=d['vp']
R=np.load('recon0302.npz'); Vh=R['Vh']; f=float(R['f'])
c=np.array([1280.,720.])
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0302.mp4')
fr=[];i=0
while True:
    ok,F=cap.read()
    if not ok: break
    if 51<=i<=71: fr.append(F)
    i+=1
tips=[]
for k,F in enumerate(fr):
    dd=np.abs(F.astype(np.float32)-bg).sum(2)
    for thr in (40,):
        m=(dd>thr).astype(np.uint8)
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        kk=1+np.argmax(st[1:,4]); m=(lab==kk)
    ys,xs=np.nonzero(m)
    P=np.stack([xs,ys],1).astype(float)
    # tail direction in image: roughly radial away from vp, with tail lying at angle ~32 deg; restrict to region right-below of head
    D=P-vp; ang=np.degrees(np.arctan2(D[:,1],D[:,0])); r=np.linalg.norm(D,axis=1)
    # choose points in tail angular window and take max radius
    sel=(ang>31.0)&(ang<34.5)
    j=np.argmax(np.where(sel,r,-1))
    tips.append(P[j])
tips=np.array(tips); t=np.arange(51,72)/24.
r=np.linalg.norm(tips-vp,axis=1)
A=np.polyfit(t,1/r,1); s_tip=-A[1]/A[0]
print('tail tip px frame51',tips[0],'frame71',tips[-1])
print('1/r fit residual px',np.abs(1/np.polyval(A,t)-r).max(),'t*_tip',s_tip)
Vz=1.29*Vh[2]
Z=Vz*(t[0]-s_tip); X=np.array([Z*(tips[0,0]-c[0])/f, Z*(tips[0,1]-c[1])/f, Z])
a_tip=X@Vh
amax=R['a'].max()
print('a_tip rel amax',a_tip-amax)
# head-patch points: bright grey patch; find its tracked points
a=R['a']; T=d['T']
# head patch region at frame 51 approx (1020-1060, 390-430)
hp=(T[0,:,0]>1005)&(T[0,:,0]<1075)&(T[0,:,1]>380)&(T[0,:,1]<440)
print('head-region tracks',hp.sum(),'a rel amax',np.sort(a[hp]-amax))
# per-frame tip ang check
print('angles of tip', np.degrees(np.arctan2(*(tips-vp)[:,::-1].T))[:5])
np.save('tips0302.npy',tips)
