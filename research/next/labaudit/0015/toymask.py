import cv2, numpy as np
from extract import load
fr=load('x'); ims=[]
prev=None
for i in range(58,70):
    f=fr[i]; hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV).astype(int)
    m=(hsv[...,0]>=8)&(hsv[...,0]<=22)&(hsv[...,1]>110)&(hsv[...,2]<170)
    m[:, :400]=False; m[:100]=False; m[420:]=False
    m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); ys,xs=np.nonzero(lab==k)
    c=(xs.mean(),ys.mean())
    d='' if prev is None else f'step {np.hypot(c[0]-prev[0],c[1]-prev[1]):.1f} dy {c[1]-prev[1]:.1f}'
    print(i, f'c=({c[0]:.1f},{c[1]:.1f}) top {ys.min()} bot {ys.max()} area {len(xs)}', d)
    prev=c
    v=f[100:420,360:520].copy(); v[m[100:420,360:520]>0]=(255,0,255)
    cv2.putText(v,str(i),(3,15),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),1); ims.append(v)
cv2.imwrite('toymask_58_69.jpg',np.hstack(ims))
