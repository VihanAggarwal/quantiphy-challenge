import cv2, numpy as np
fr=cv2.imread('others/captured_0024_48.png'); hsv=cv2.cvtColor(fr,cv2.COLOR_BGR2HSV).astype(int)
m=((hsv[...,0]>=80)&(hsv[...,0]<=110)&(hsv[...,1]>=25)&(hsv[...,2]>=120)).astype(np.uint8)
m[:400]=0; m[560:]=0; m[:,:450]=0; m[:,700:]=0
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
n,lab,st,cen=cv2.connectedComponentsWithStats(m); k=1+np.argmax(st[1:,4]); m=(lab==k).astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
ys,xs=np.nonzero(m); print('area',len(xs),'x',xs.min(),xs.max(),'y',ys.min(),ys.max())
cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); c=max(cs,key=cv2.contourArea)
for eps in [2,3,4,6]:
    ap=cv2.approxPolyDP(c,eps,True); print(eps, ap.reshape(-1,2).tolist())
vis=fr.copy(); vis[m>0]=(0.5*vis[m>0]+[0,0,127]).astype(np.uint8)
cv2.imwrite('others/v24_covermask.png',cv2.resize(vis[420:540,440:720],None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST))
np.save('others/v24_cover.npy',m)
