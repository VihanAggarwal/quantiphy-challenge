import cv2, numpy as np, sys
sys.path.insert(0,'scripts')
from cam import *
def frames(v):
    cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4'%v)
    out=[]
    while True:
        ok,f=cap.read()
        if not ok: break
        out.append(f)
    return out
a=frames('simulation_0211')
bg=np.median(np.stack(a[::2]),axis=0).astype(np.uint8)
rows=[]
for i,fr in enumerate(a):
    d=np.abs(fr.astype(int)-bg.astype(int)).sum(2)
    hsv=cv2.cvtColor(fr,cv2.COLOR_BGR2HSV)
    m=((d>60)&(hsv[...,2]<90)).astype(np.uint8)  # black fur
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); mm=lab==k
    ys,xs=np.nonzero(mm)
    rows.append((i,xs.min(),xs.max(),xs.mean(),ys.mean(),ys.max()))
R=np.array(rows,float)
np.save('cat0211.npy',R)
for c0 in [3.9,4.0,4.1]:
    A=a_from_u(R[:,3],c0)
    t=R[:,0]/24
    p=np.polyfit(t,A,1)
    print('c0',c0,'fit speed',p[0],'a0',p[1], 'resid',np.std(A-np.polyval(p,t)))
    for hz in [0.0,0.15,0.25]:
        print('   hz',hz,'r(0)',rng(p[1],c0,hz),'r(1)',rng(p[1]+p[0],c0,hz))
