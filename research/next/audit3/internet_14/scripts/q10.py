import cv2,numpy as np
c=cv2.VideoCapture('data/QuantiPhy/internet_0010.mp4')
F={}
k=0
while True:
    ok,im=c.read()
    if not ok: break
    if 44<=k<=80: F[k]=im
    k+=1
prev=None
pos={}
for k in sorted(F):
    im=F[k]
    hsv=cv2.cvtColor(im[0:1500],cv2.COLOR_BGR2HSV)
    # sky is blue (H~100-120); ball orange-brown H 5-25, S>80
    m=((hsv[...,0]>=3)&(hsv[...,0]<=25)&(hsv[...,1]>70)&(hsv[...,2]>40)&(hsv[...,2]<220)).astype(np.uint8)
    # restrict to sky region: blue neighbourhood -> require pixels above y<1300
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    cands=[(i,st[i],cen[i]) for i in range(1,n) if 800<st[i,4]<4000 and 0.6<st[i,2]/max(1,st[i,3])<1.6 and st[i,2]<80]
    if prev is not None:
        cands=[cc for cc in cands if np.hypot(cc[2][0]-prev[0],cc[2][1]-prev[1])<150]
    if cands:
        best=max(cands,key=lambda t:t[1][4])
        prev=best[2]; pos[k]=best[2]
        print(k, np.round(best[2],1), best[1][2:5])
    else: print(k,'none')
# camera: phase correlation on lower static background (buildings band) between consecutive frames
for k in (56,58,60,62,64):
    a=np.float32(cv2.cvtColor(F[k][1100:1500,0:3840],cv2.COLOR_BGR2GRAY)); b=np.float32(cv2.cvtColor(F[k+1][1100:1500,0:3840],cv2.COLOR_BGR2GRAY))
    print('cam',k,cv2.phaseCorrelate(a,b))
