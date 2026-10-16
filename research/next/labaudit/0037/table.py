"""Table-plane pose for captured_0037 from the table outline (x render, frame 24), f=711, pp=(640,360)."""
import cv2, numpy as np
F=711.0; CX,CY=640.,360.
f=cv2.imread('/home/user/quantiphy-challenge/research/next/labaudit/0037/frames/vx_24.png').astype(float)
m=f.sum(2)>60
g=cv2.GaussianBlur(f.mean(2),(5,5),0); dy=np.diff(g,axis=0)
def top(x):
    col=np.where(m[430:640,x])[0]; return 430+col.min()
L=[(x,top(x)) for x in range(220,430,5)]
R=[(x,top(x)) for x in range(935,1130,5)]
B=[(x,top(x)) for x in list(range(605,655,3))+list(range(820,905,3))]
Fr=[]
for x in list(range(240,560,10))+list(range(700,1100,10)):
    d=dy[515:600,x]; Fr.append((x,515+np.argmin(d)+0.5))
def fit(pts):
    p=np.array(pts,float)
    for it in range(4):
        A=np.c_[p[:,0],np.ones(len(p))]; k,b=np.linalg.lstsq(A,p[:,1],rcond=None)[0]
        res=p[:,1]-(k*p[:,0]+b); keep=np.abs(res)<max(2.0,3*np.median(np.abs(res)))
        p=p[keep]
    return k,b,np.abs(res[keep]).max()
lines={n:fit(p) for n,p in dict(L=L,R=R,B=B,F=Fr).items()}
print({n:(round(k,4),round(b,1),round(r,1)) for n,(k,b,r) in lines.items()})
print('B pts',B[:5],B[-5:])
def inter(a,b):
    k1,b1,_=lines[a];k2,b2,_=lines[b]; x=(b2-b1)/(k1-k2); return np.array([x,k1*x+b1])
C={'FL':inter('F','L'),'FR':inter('F','R'),'BR':inter('B','R'),'BL':inter('B','L')}
print({k:v.round(1) for k,v in C.items()})
def ray(p): return np.array([(p[0]-CX)/F,(p[1]-CY)/F,1.0])
# vanishing points
def vp(a,b):
    k1,b1,_=lines[a];k2,b2,_=lines[b]; x=(b2-b1)/(k1-k2); return np.array([x,k1*x+b1])
V1=vp('F','B'); V2=vp('L','R')
d1=ray(V1); d1/=np.linalg.norm(d1); d2=ray(V2); d2/=np.linalg.norm(d2)
print('VP',V1.round(0),V2.round(0),'orthogonality cos',d1@d2)
n=np.cross(d1,d2); n/=np.linalg.norm(n)
if n[1]>0: n=-n   # normal pointing up (camera y down)
print('normal',n.round(4),'tilt deg',np.degrees(np.arccos(abs(n[1]))))
# plane n.X = -h  ; points X = s*ray ; s = -h/(n.ray)
def onplane(p,h=1.0): r=ray(p); return r*(-h/(n@r))
P={k:onplane(v) for k,v in C.items()}
front=np.linalg.norm(P['FR']-P['FL']); back=np.linalg.norm(P['BR']-P['BL']); left=np.linalg.norm(P['BL']-P['FL']); right=np.linalg.norm(P['BR']-P['FR'])
print('unit-h sides front back left right',front,back,left,right,'aspect',(front+back)/(left+right))
# scale: front/back = 76.0 or 60.3 ?
for W in (76.0,60.3):
    h=W/100/((front+back)/2); print('if front=%.1f: cam height above table %.3f m, side=%.1f cm'%(W,h,(left+right)/2*h*100))
np.save('/home/user/quantiphy-challenge/research/next/labaudit/0037/plane.npy',n)
