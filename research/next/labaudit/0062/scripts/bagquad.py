import numpy as np, cv2
from common import *
exec(open('objrect.py').read().split('for f,(p,r)')[0])
o=load('')
med=np.median(o[0:49:2].astype(float),0).astype(np.uint8)
bag=comp_at(837,329)
nrm=normal(38.93,8.53)
L,W,mo=rect_on_plane(bag,nrm,0.0,F,9)
cs,_=cv2.findContours(mo,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); c=max(cs,key=cv2.contourArea).reshape(-1,2).astype(float)
hull=cv2.convexHull(c.astype(np.float32)).reshape(-1,2); peri=cv2.arcLength(hull.reshape(-1,1,2),True)
for eps in np.linspace(0.01,0.1,50):
    ap=cv2.approxPolyDP(hull.reshape(-1,1,2),eps*peri,True).reshape(-1,2)
    if len(ap)<=4: break
print('approx quad',ap)
def fitline(pts):
    cc=pts.mean(0); u,s,vt=np.linalg.svd(pts-cc); d=vt[0]; nn=np.array([-d[1],d[0]]); return np.array([nn[0],nn[1],-nn@cc])
lines=[]
for i in range(4):
    a,b=ap[i],ap[(i+1)%4]; ab=b-a; Ln=np.linalg.norm(ab); u=ab/Ln; nn=np.array([-u[1],u[0]])
    t=(c-a)@u; d=(c-a)@nn; P=c[(t>0.2*Ln)&(t<0.8*Ln)&(np.abs(d)<15)]
    for it in range(5):
        l=fitline(P); rr=P@l[:2]+l[2]; P=P[np.abs(rr-np.median(rr))<2]
    lines.append(l)
cor=[]
for i in range(4):
    p=np.cross(lines[i-1],lines[i]); cor.append(p[:2]/p[2])
cor=np.array(cor); print('corners',np.round(cor,1))
for f,(p,r) in {700:(39.34,8.43),711:(38.93,8.53),722:(38.50,8.66)}.items():
    nm=normal(p,r); s,cs_,_=geom(cor,nm,1.0,f)
    print(f,'sides/h',np.round(s,4),'cos',np.round(cs_,3))
x0,y0,x1,y1=740,260,930,400; sc=4
crop=cv2.resize(med[y0:y1,x0:x1],None,fx=sc,fy=sc,interpolation=cv2.INTER_CUBIC)
cc=((c-[x0,y0])*sc).astype(np.int32); cv2.polylines(crop,[cc.reshape(-1,1,2)],True,(0,255,255),1)
q=((cor-[x0,y0])*sc).astype(np.int32); cv2.polylines(crop,[q.reshape(-1,1,2)],True,(0,0,255),2)
cv2.imwrite(O+'frames/bag_quad.jpg',crop,[cv2.IMWRITE_JPEG_QUALITY,90])
