# Track the ping-pong ball in internet_0044 (static camera): median background, white-ish moving blob.
import cv2, numpy as np
P='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0044.mp4'
c=cv2.VideoCapture(P); F=[]
while True:
    ok,im=c.read()
    if not ok: break
    F.append(cv2.resize(im,(960,540),interpolation=cv2.INTER_AREA))   # half res in RAM only
F=np.array(F); N=len(F)
bg=np.median(F[::3],axis=0).astype(np.int16)
rows=[]
for i in range(N):
    im=F[i].astype(np.int16)
    d=np.abs(im-bg).max(2)
    hsv=cv2.cvtColor(F[i],cv2.COLOR_BGR2HSV)
    white=(hsv[...,1]<70)&(hsv[...,2]>150)
    m=((d>40)&white).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    best=None
    for k in range(1,n):
        x,y,w,h,a=st[k]
        if 120<a<2500 and 0.6<w/h<1.6 and a>0.5*w*h:
            if best is None or a>best[4]: best=(x,y,w,h,a,cen[k][0],cen[k][1])
    rows.append((i,)+(best if best else (np.nan,)*7))
R=np.array(rows,float)
np.save('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/i02/ball44.npy',R)
for r in R[::3]: print(int(r[0]), np.round(r[1:],1))
