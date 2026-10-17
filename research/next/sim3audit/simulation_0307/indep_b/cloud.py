import numpy as np, cv2
from recon import *
f=3575.; N=24; Vz=18.49; vzf=Vz/N; iref=24
e3=np.array([E[0]-C[0],E[1]-C[1],f]); V=e3/np.linalg.norm(e3)
phi=np.arctan2(C[1]-E[1],f)  # pitch so that FOE on horizon
up=np.array([0,-np.cos(phi),-np.sin(phi)])
up=up-V*(up@V); up/=np.linalg.norm(up)
S=np.cross(V,up); S/=np.linalg.norm(S)   # check sign later
U=np.cross(S,V)
pts=[];src=[]
for c in ['0303','0305','0307']:
    P=np.load(f'tracks_{c}.npy')
    for t in fitq(P):
        if t['res']>1.5 or t['perp']>1.5: continue
        X,x=pos3d(t,f,iref,vzf)
        pts.append(np.r_[X,x]); src.append(c)
pts=np.array(pts)
X=pts[:,:3]
cen=X.mean(0)
loc=np.c_[(X-cen)@V,(X-cen)@S,(X-cen)@U]
print('n',len(X),'S',S,'U',U,'V',V)
print('fore range',loc[:,0].min(),loc[:,0].max(),'span',loc[:,1].min(),loc[:,1].max(),'up',loc[:,2].min(),loc[:,2].max())
np.save('cloud.npy',np.c_[loc,pts[:,3:]])
# plot top view and side view
img=np.full((800,1600,3),255,np.uint8)
def tv(a,b,ox,oy,sc): return (int(ox+a*sc),int(oy-b*sc))
for l in loc:
    cv2.circle(img,tv(l[1],l[0],400,400,30),3,(0,0,255),-1)   # top: x=span, y=fore
    cv2.circle(img,tv(l[0],l[2],1200,400,30),3,(255,0,0),-1)  # side: x=fore, y=up
for k in range(-12,13,2):
    cv2.line(img,tv(k,-12,400,400,30),tv(k,12,400,400,30),(220,220,220),1)
    cv2.line(img,tv(-12,k,400,400,30),tv(12,k,400,400,30),(220,220,220),1)
    cv2.line(img,tv(k,-12,1200,400,30),tv(k,12,1200,400,30),(220,220,220),1)
    cv2.line(img,tv(-12,k,1200,400,30),tv(12,k,1200,400,30),(220,220,220),1)
cv2.imwrite('fr/cloud.png',img)
