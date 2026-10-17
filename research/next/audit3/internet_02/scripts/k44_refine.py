# Full-res ball centroid for frames 40..100 of internet_0044 (crop around half-res detection, bg-subtracted white blob)
import cv2, numpy as np
P='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0044.mp4'
R=np.load('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/i02/ball44.npy')
c=cv2.VideoCapture(P); F={}; bgf=[]; i=0
while True:
    ok,im=c.read()
    if not ok: break
    if i%6==0: bgf.append(im)
    if 40<=i<=100: F[i]=im
    i+=1
bg=np.median(np.array(bgf),axis=0).astype(np.int16)
out={}
for i in range(41,101):
    if np.isnan(R[i,6]): continue
    cx,cy=R[i,6]*2,R[i,7]*2
    x0=int(max(0,cx-80)); y0=int(max(0,cy-90)); x1=int(min(1920,cx+80)); y1=int(min(1080,cy+90))
    im=F[i][y0:y1,x0:x1]; d=np.abs(im.astype(np.int16)-bg[y0:y1,x0:x1]).max(2)
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    m=((d>35)&(hsv[...,1]<80)&(hsv[...,2]>140)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    out[i]=(x0+cen[k][0],y0+cen[k][1],w,h)
np.save('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/i02/ball44_full.npy',np.array([(k,)+v for k,v in out.items()]))
for k in sorted(out):
    if 41<=k<=50 or 70<=k<=82: print(k,np.round(out[k],1))
