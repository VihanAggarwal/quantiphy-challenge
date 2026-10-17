import cv2,numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0024.mp4')
ok,f=c.read()
roi=f[750:1250,2350:2850]
hsv=cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
m=((hsv[:,:,1]<40)&(hsv[:,:,2]>170)).astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
n,lab,st,cen=cv2.connectedComponentsWithStats(m)
j=1+np.argmax(st[1:,4])
cnt,_=cv2.findContours((lab==j).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
r=cv2.minAreaRect(cnt[0]); print('minAreaRect',r, 'area',st[j,4])
for thr in (150,180,200):
    m=((hsv[:,:,1]<50)&(hsv[:,:,2]>thr)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m); j=1+np.argmax(st[1:,4])
    cnt,_=cv2.findContours((lab==j).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    print(thr,cv2.minAreaRect(cnt[0]))
cv2.imwrite('c24_case.png',cv2.resize(roi,None,fx=0.8,fy=0.8))
