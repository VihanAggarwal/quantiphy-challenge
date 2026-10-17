import cv2,numpy as np
W='/home/user/quantiphy-challenge/research/next/labaudit2/0024/remeasure_work'
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0024x.mp4')
fr=[]
while True:
    ok,f=cap.read()
    if not ok: break
    fr.append(f)
print(len(fr))
F=fr[0]
m=(F.max(axis=2)>35).astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
H,Wd=m.shape
def top(x):
    ys=np.where(m[430:700,x]>0)[0]
    return 430+ys.min() if len(ys) else None
def bot(x):
    ys=np.where(m[430:640,x]>0)[0]
    return 430+ys.max() if len(ys) else None
def fit(xs,fn):
    pts=[(x,fn(x)) for x in xs if fn(x) is not None]
    pts=np.array(pts,float)
    A=np.c_[pts[:,0],np.ones(len(pts))]
    k,b=np.linalg.lstsq(A,pts[:,1],rcond=None)[0]
    r=pts[:,1]-(k*pts[:,0]+b)
    return k,b,np.abs(r).max()
# far-left edge: top boundary x 425..590
for name,xs,fn in [('farleft top',range(425,595,2),top),('farright top',range(880,1090,2),top),
                   ('frontleft bottom',range(430,630,2),bot),('frontright bottom',range(660,1000,2),bot)]:
    print(name,fit(xs,fn))
for x in range(860,1140,20): print(x,top(x),bot(x))
print('---')
xs=list(range(660,740,2))+list(range(805,1080,2))
k4,b4,r4=fit(xs,bot); print('frontright bottom (no leg)',k4,b4,r4)
k1,b1,_=fit(range(425,595,2),top)   # far-left (dir FR)
k2,b2,_=fit(range(880,1090,2),top)  # far-right (dir LF)
k3,b3,_=fit(range(430,630,2),bot)   # front-left bottom (dir LF)
def inter(ka,ba,kb,bb):
    x=(bb-ba)/(ka-kb); return np.array([x,ka*x+ba])
VP_FR=inter(k1,b1,k4,b4); VP_LF=inter(k2,b2,k3,b3)
print('VP of FR dir',VP_FR,'VP of LF dir',VP_LF)
c=np.array([640,360.])
f2=-(VP_FR-c)@(VP_LF-c)
print('implied f',np.sqrt(f2) if f2>0 else f2)
# horizon line through both VPs
hk=(VP_LF[1]-VP_FR[1])/(VP_LF[0]-VP_FR[0]); print('horizon slope',hk,'y at cx',VP_FR[1]+hk*(640-VP_FR[0]))
# corners: L = farleft ∩ frontleft(top). Use bottom lines intersections for bottom corners
print('L(bottom-ish) farleft∩frontleftbottom',inter(k1,b1,k3,b3))
print('R farright∩frontrightbottom',inter(k2,b2,k4,b4))
print('F bottom frontleftbottom∩frontrightbottom',inter(k3,b3,k4,b4))
print('B farleft∩farright',inter(k1,b1,k2,b2))
