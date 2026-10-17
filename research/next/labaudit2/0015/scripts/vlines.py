import cv2, numpy as np
from common import load, F, CX, CY
f=load('o')[0]
g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
e=cv2.Canny(cv2.GaussianBlur(g,(5,5),0),10,30)
e[:, 250:520]=0   # person
L=cv2.HoughLinesP(e,1,np.pi/1440,60,minLineLength=120,maxLineGap=10)
segs=[]
vis=f.copy()
for x1,y1,x2,y2 in L.reshape(-1,4):
    if abs(x2-x1)<0.2*abs(y2-y1):
        segs.append((x1,y1,x2,y2)); cv2.line(vis,(x1,y1),(x2,y2),(0,0,255),2)
segs=np.array(segs,float)
print(len(segs))
for s in segs: print(s.astype(int), 'dx/dy %.4f'%((s[2]-s[0])/(s[3]-s[1])))
# vanishing point via least squares on homogeneous lines
Ls=[]
for x1,y1,x2,y2 in segs:
    l=np.cross([x1,y1,1],[x2,y2,1]); l/=np.hypot(l[0],l[1]); Ls.append(l*np.hypot(x2-x1,y2-y1))
Ls=np.array(Ls)
U,S,Vt=np.linalg.svd(Ls); vp=Vt[-1]; 
print('vp homog',vp, 'vp px',vp[:2]/vp[2] if abs(vp[2])>1e-9 else 'inf')
d=np.array([vp[0]-CX*vp[2],vp[1]-CY*vp[2],F*vp[2]]); d/=np.linalg.norm(d)
if d[1]<0: d=-d
print('vertical (down) direction in camera frame', d.round(4), 'pitch deg (positive = camera looks down)', np.degrees(np.arcsin(-d[2])).round(2) if True else '', 'roll deg', np.degrees(np.arctan2(d[0],d[1])).round(2))
cv2.imwrite('../img/vlines_o0.jpg',vis)
