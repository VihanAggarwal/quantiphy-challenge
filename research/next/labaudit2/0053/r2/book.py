import cv2,numpy as np
med=cv2.imread('median0053.png').astype(float)
x0,y0=600,560
c=med[y0:y0+110,x0:x0+130]
g=c.min(2)
m=(g>165).astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
n,lab,st,cen=cv2.connectedComponentsWithStats(m)
k=1+np.argmax(st[1:,4]); bm=(lab==k).astype(np.uint8)
cnt=max(cv2.findContours(bm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)[0],key=cv2.contourArea)
hull=cv2.convexHull(cnt)
for eps in [2,3,4]:
    ap=cv2.approxPolyDP(hull,eps,True).reshape(-1,2)
    print(eps,(ap+[x0,y0]).tolist())
cv2.imwrite('bookmask.png',cv2.resize(bm*255,None,fx=4,fy=4,interpolation=cv2.INTER_NEAREST))
np.save('bookcnt.npy',cnt.reshape(-1,2)+[x0,y0])
