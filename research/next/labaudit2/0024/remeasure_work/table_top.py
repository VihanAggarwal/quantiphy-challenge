import cv2,numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0024x.mp4')
ok,F=cap.read()
g=cv2.GaussianBlur(cv2.cvtColor(F,cv2.COLOR_BGR2GRAY).astype(float),(3,3),0)
m=(F.max(axis=2)>35)
def edge_in(x,y0,y1):
    col=g[y0:y1,x]
    d=col[2:]-col[:-2]   # top surface lighter -> front face darker => negative gradient
    i=np.argmin(d); return y0+1+i, d[i]
pts=[]
for x in list(range(430,630,4)):
    ys=np.where(m[430:640,x])[0]; t=430+ys.min(); b=430+ys.max()
    y,dv=edge_in(x,t+3,b-3); pts.append((x,y,dv,t,b))
pts=np.array(pts,float)
A=np.c_[pts[:,0],np.ones(len(pts))]
k,bb=np.linalg.lstsq(A,pts[:,1],rcond=None)[0]; print('front-left top edge',k,bb,'resid',np.abs(pts[:,1]-(k*pts[:,0]+bb)).max())
print(pts[::5])
pts=[]
for x in list(range(660,740,4))+list(range(805,1080,4)):
    ys=np.where(m[430:640,x])[0]; t=430+ys.min(); b=430+ys.max()
    y,dv=edge_in(x,t+3,b-3); pts.append((x,y,dv,t,b))
pts=np.array(pts,float)
A=np.c_[pts[:,0],np.ones(len(pts))]
k2,b2=np.linalg.lstsq(A,pts[:,1],rcond=None)[0]; print('front-right top edge',k2,b2,'resid',np.abs(pts[:,1]-(k2*pts[:,0]+b2)).max())
print(pts[::5])
x=(b2-bb)/(k-k2); print('F top corner',x,k*x+bb)
print('=== robust')
def fitr(xs):
    P=[]
    for x in xs:
        ys=np.where(m[430:640,x])[0]; t=430+ys.min(); b=430+ys.max()
        y,dv=edge_in(x,t+3,b-3); P.append((x,y))
    P=np.array(P,float)
    for it in range(3):
        A=np.c_[P[:,0],np.ones(len(P))]
        k,b=np.linalg.lstsq(A,P[:,1],rcond=None)[0]
        r=np.abs(P[:,1]-(k*P[:,0]+b)); P=P[r<max(2,np.percentile(r,80))]
    return k,b,r.max() if len(r) else 0
kL,bL,_=fitr(range(430,592,2)); kR,bR,_=fitr(range(865,1070,2))
print('front-left top',kL,bL,' front-right top',kR,bR)
x=(bR-bL)/(kL-kR); print('F top corner',x,kL*x+bL)
# far-left top line and far-right top line (outline)
def topo(x):
    ys=np.where(m[430:700,x])[0]; return 430+ys.min()
def fitl(xs,fn):
    P=np.array([(x,fn(x)) for x in xs],float); A=np.c_[P[:,0],np.ones(len(P))]
    return np.linalg.lstsq(A,P[:,1],rcond=None)[0]
k1,b1=fitl(range(425,595,2),topo); k2,b2=fitl(range(880,1090,2),topo)
xL=(b1-bL)/(kL-k1); print('L top corner',xL,kL*xL+bL)
xR=(b2-bR)/(kR-k2); print('R top corner',xR,kR*xR+bR)
xB=(b2-b1)/(k1-k2); print('B corner',xB,k1*xB+b1)
VP1x=(bR-b1)/(k1-kR); VP2x=(b2-bL)/(kL-k2)
V1=np.array([VP1x,k1*VP1x+b1]); V2=np.array([VP2x,kL*VP2x+bL]); print('VPs',V1,V2)
c=np.array([640,360.]); f2=-(V1-c)@(V2-c); print('implied f (top lines)',np.sqrt(abs(f2)),np.sign(f2))
np.save('/home/user/quantiphy-challenge/research/next/labaudit2/0024/remeasure_work/table_lines.npy',np.array([[k1,b1],[k2,b2],[kL,bL],[kR,bR]]))
