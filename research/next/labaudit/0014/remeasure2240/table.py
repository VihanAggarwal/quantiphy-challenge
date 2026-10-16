import cv2,numpy as np
f=cv2.imread('frames/captured_0014s_40.png')
hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
g=f.astype(int)
green=(g[:,:,1]>g[:,:,2]+15)&(g[:,:,1]>g[:,:,0]+15)
m=(~green).astype(np.uint8)
m[690:,:]=0  # watermark
m[:,:300]=0; m[:,900:]=0
n,lab,st,cen=cv2.connectedComponentsWithStats(m)
k=1+np.argmax(st[1:,4]); M=(lab==k).astype(np.uint8)
# remove pedestal: rows below 480 narrow part
cnts,_=cv2.findContours(M,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
c=max(cnts,key=cv2.contourArea)
hull=cv2.convexHull(c)
for eps in [3,5,8,12]:
    ap=cv2.approxPolyDP(hull,eps,True)
    print(eps,ap.reshape(-1,2).tolist())
cv2.imwrite('table_mask.png',M*255)
