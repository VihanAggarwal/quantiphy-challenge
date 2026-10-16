import sys, cv2, numpy as np; sys.path.insert(0,'scripts')
from geo import *
im=cv2.imread('other/0062x_34.png').astype(int)
m=(im.sum(2)>40).astype(np.uint8); m[690:,1000:]=0
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
k,lab,st,cen=cv2.connectedComponentsWithStats(m)
i=[j for j in range(1,k) if st[j][4]>20000][0]
mm=(lab==i).astype(np.uint8)
cs,_=cv2.findContours(mm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); c=max(cs,key=cv2.contourArea)
for e in np.arange(2,30,0.5):
    ap=cv2.approxPolyDP(c,e,True)
    if len(ap)==4: break
quad=ap.reshape(-1,2).astype(float); print('quad',quad.tolist(),'eps',e)
# refine: fit lines to contour points near each side
cpts=c.reshape(-1,2).astype(float)
lines=[]
for j in range(4):
    p0=quad[j]; p1=quad[(j+1)%4]
    d=p1-p0; L=np.linalg.norm(d); d/=L; nrm=np.array([-d[1],d[0]])
    t=(cpts-p0)@d; s=(cpts-p0)@nrm
    sel=(t>0.15*L)&(t<0.85*L)&(np.abs(s)<4)
    q=cpts[sel]; mu=q.mean(0); U,S,Vt=np.linalg.svd(q-mu); dd=Vt[0]
    lines.append((mu,dd))
corn=[]
for j in range(4):
    (m1,d1),(m2,d2)=lines[j-1],lines[j]
    A=np.c_[d1,-d2]; t=np.linalg.solve(A,m2-m1); corn.append(m1+t[0]*d1)
corn=np.array(corn); print('refined corners',np.round(corn,1).tolist())
for name,dn,H in [('roll',DOWN_ROLL,1.689),('noroll',DOWN_NOROLL,1.711)]:
    Q=np.array([floor_pt(u,v,H,dn,0.005) for u,v in corn])
    e=[np.linalg.norm(Q[(j+1)%4]-Q[j]) for j in range(4)]
    ang=[np.degrees(np.arccos((Q[j-1]-Q[j])@(Q[(j+1)%4]-Q[j])/np.linalg.norm(Q[j-1]-Q[j])/np.linalg.norm(Q[(j+1)%4]-Q[j]))) for j in range(4)]
    print(name,'edges cm',np.round(np.array(e)*100,1),'angles',np.round(ang,1))
np.save('wb62_corners.npy',corn)
