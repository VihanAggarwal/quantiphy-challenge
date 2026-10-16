import cv2, numpy as np
# whiteboard mask from x render (black bg): bright, low saturation, large component
for i in range(49):
    f=cv2.imread('frames/x_%02d.png'%i)
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    m=((hsv[...,2]>170)&(hsv[...,1]<40)).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    j=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[j]
    mm=(lab==j).astype(np.uint8)
    cnts,_=cv2.findContours(mm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cnts,key=cv2.contourArea)
    hull=cv2.convexHull(c)
    ap=cv2.approxPolyDP(hull,0.02*cv2.arcLength(hull,True),True)
    print(i, 'bbox',x,y,w,h,'area',a,'cent',np.round(cen[j],1),'poly',ap.reshape(-1,2).tolist())
