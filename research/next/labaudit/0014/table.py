import cv2, numpy as np
im=cv2.imread('frames/rs_40.png')
hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
# background green: hue ~ 50-80
g=((hsv[...,0]>35)&(hsv[...,0]<90)&(hsv[...,1]>80)).astype(np.uint8)
fg=1-g
fg[540:]=0  # remove leg region below table-ish
fg=cv2.morphologyEx(fg,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
n,lab,st,cen=cv2.connectedComponentsWithStats(fg)
k=1+np.argmax(st[1:,4]); m=(lab==k).astype(np.uint8)
cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
c=max(cnts,key=cv2.contourArea)
hull=cv2.convexHull(c)
ap=cv2.approxPolyDP(hull,4,True)
print(ap.reshape(-1,2))
vis=im.copy(); cv2.drawContours(vis,[ap],-1,(0,0,255),1)
cv2.imwrite('table_poly.png',vis[250:560,380:780])
