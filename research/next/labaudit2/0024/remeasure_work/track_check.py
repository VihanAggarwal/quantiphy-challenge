import cv2,numpy as np,sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0024/remeasure_work')
import rect
f=711.
def K1(u,v): return np.array([(u-640)/f,(v-360)/f,1.])
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0024x.mp4'); fr=[]
while True:
    ok,im=cap.read()
    if not ok: break
    fr.append(im)
rect.f=f
r_,P=rect.rect((606.6,467.5),(708.0,492.5),(862.7,361.5),(751.1,360.1),verbose=False); P=np.array(P)
s=0.99/np.linalg.norm((P[0]+P[1])/2); P=P*s
n=np.cross(P[1]-P[0],P[3]-P[0]); n/=np.linalg.norm(n); d=n@P[0]
if d>0: n,d=-n,-d
T=0.014
prev=None
for k in range(14,34):
    hsv=cv2.cvtColor(fr[k],cv2.COLOR_BGR2HSV).astype(int)
    m=((hsv[...,0]>=75)&(hsv[...,0]<=100)&(hsv[...,1]>=20)&(hsv[...,2]>120)).astype(np.uint8)
    m[:300]=0;m[520:]=0;m[:,:450]=0;m[:,900:]=0
    nlab,lab,st,cen=cv2.connectedComponentsWithStats(m)
    i=1+np.argmax(st[1:,4]); cx,cy=cen[i]
    rr=K1(cx,cy); t=(d+T)/(n@rr); X=t*rr
    step='' if prev is None else '%.2f cm'%(np.linalg.norm(X-prev)*100)
    print(k,'centroid (%.1f,%.1f) area %d range on slope-plane %.4f step %s'%(cx,cy,st[i,4],np.linalg.norm(X),step))
    prev=X
