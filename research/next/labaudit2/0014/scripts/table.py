import cv2, numpy as np, sys, json
sys.path.insert(0,'scripts')
from frames import load
fr=load('x')
im=np.median(np.stack([f.astype(np.float32) for f in fr[30:49]]),0)
g=im.mean(2); hsv=cv2.cvtColor(im.astype(np.uint8),cv2.COLOR_BGR2HSV)
nonwhite=(np.abs(im-255).sum(2)>60)
# left boundary rows 400-488
L=[];R=[];Bk=[];Fr=[]
for y in range(405,488):
    xs=np.nonzero(nonwhite[y,380:560])[0]
    if len(xs): L.append((380+xs[0],y))
for y in range(318,450):
    xs=np.nonzero(nonwhite[y,600:780])[0]
    if len(xs): R.append((600+xs[-1],y))
for x in range(605,650):
    ys=np.nonzero(nonwhite[280:360,x])[0]
    if len(ys): Bk.append((x,280+ys[0]))
# front top boundary: strong vertical darkening (top surface light -> band dark) for x 445..715
V=hsv[...,2].astype(float)
for x in range(445,716,2):
    col=V[440:520,x]
    dv=col[2:]-col[:-2]
    j=np.argmin(dv)
    Fr.append((x,440+j+1))
def fit(P):
    P=np.array(P,np.float32)
    for it in range(3):
        vx,vy,x0,y0=cv2.fitLine(P,cv2.DIST_HUBER,0,0.01,0.01).ravel()
        n=np.array([-vy,vx]); d=(P-np.array([x0,y0]))@n
        P=P[np.abs(d)<2.0] if it<2 else P
    return np.array([x0,y0]),np.array([vx,vy]),float(np.sqrt(np.mean(d**2)))
lines={k:fit(v) for k,v in dict(L=L,R=R,B=Bk,F=Fr).items()}
for k,(p,d,e) in lines.items(): print(k,'pt',np.round(p,1),'dir',np.round(d,4),'rms',round(e,2))
def X(a,b):
    (p1,d1,_),(p2,d2,_)=lines[a],lines[b]
    s=np.linalg.solve(np.array([d1,-d2]).T,p2-p1); return p1+s[0]*d1
C={'FL':X('L','F'),'FR':X('F','R'),'BR':X('R','B'),'BL':X('B','L')}
for k,v in C.items(): print(k,np.round(v,1))
json.dump({k:v.tolist() for k,v in C.items()},open('table_corners.json','w'))
