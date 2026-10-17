import cv2, numpy as np
from cyl import pose, ray_plane
med=cv2.imread('median_x.png')
hsv=cv2.cvtColor(med,cv2.COLOR_BGR2HSV)
g=cv2.cvtColor(med,cv2.COLOR_BGR2GRAY)
roi=np.zeros(g.shape,bool); roi[520:560,495:630]=True
# card: dark blue or yellow sticker; wood: brownish bright
b,gg,r=[med[:,:,i].astype(int) for i in range(3)]
card=((b>r+5)|(g<90)|((r>150)&(gg>150)&(b<120)))&roi
card=card.astype(np.uint8)
card=cv2.morphologyEx(card,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
n,lab,st,cen=cv2.connectedComponentsWithStats(card)
k=1+np.argmax(st[1:,4]); cm=(lab==k).astype(np.uint8)
print('card area',st[k])
cnts,_=cv2.findContours(cm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
c=max(cnts,key=cv2.contourArea)
eps=2.0
ap=cv2.approxPolyDP(c,eps,True)
while len(ap)>4: eps+=0.5; ap=cv2.approxPolyDP(c,eps,True)
print('quad',ap.reshape(-1,2))
cv2.imwrite('card_mask.png',cv2.resize(cm[515:565,490:635]*255,None,fx=6,fy=6,interpolation=cv2.INTER_NEAREST))
# refine: fit lines to contour segments between quad corners
q=ap.reshape(-1,2).astype(float)
pts=c.reshape(-1,2).astype(float)
# assign contour points to nearest edge
lines=[]
for i in range(4):
    p0,p1=q[i],q[(i+1)%4]
    d=p1-p0; L=np.linalg.norm(d); d/=L; nrm=np.array([-d[1],d[0]])
    t=(pts-p0)@d; dist=np.abs((pts-p0)@nrm)
    sel=(t>0.15*L)&(t<0.85*L)&(dist<2)
    P=pts[sel]; mu=P.mean(0); U,S,Vt=np.linalg.svd(P-mu); dd=Vt[0]
    lines.append((mu,dd))
def inter(l1,l2):
    (p,d),(q_,e)=l1,l2
    A=np.c_[d,-e]; s=np.linalg.solve(A,q_-p); return p+s[0]*d
corners=[inter(lines[i-1],lines[i]) for i in range(4)]
# contour pixel boundaries are at pixel centres of boundary pixels -> half-pixel inset; expand by 0.5 px outward approx
corners=np.array(corners); cc=corners.mean(0)
corners_out=cc+(corners-cc)*(1+0.5/np.linalg.norm(corners-cc,axis=1))[:,None]
print('corners',corners.round(1))
for f in [711,740]:
    K,rv,tv,res=pose(f)
    for nm,cs in [('in',corners),('out',corners_out)]:
        P=np.array([ray_plane(K,rv,tv,u)[0] for u in cs])
        Ls=[np.linalg.norm(P[(i+1)%4]-P[i])*1000 for i in range(4)]
        print(f,nm,'edge lengths mm',np.round(Ls,1))
