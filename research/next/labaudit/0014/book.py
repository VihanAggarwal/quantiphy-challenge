import cv2, numpy as np, sys
R=sys.argv[1] if len(sys.argv)>1 else 'rs'
im=cv2.imread(f'frames/{R}_40.png')
hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
sub=hsv[370:450,610:700]
m=((sub[...,0]>80)&(sub[...,0]<110)&(sub[...,1]>25)&(sub[...,2]>150)).astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
n,lab,st,cen=cv2.connectedComponentsWithStats(m)
k=1+np.argmax(st[1:,4]); m=(lab==k).astype(np.uint8)
cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
c=max(cnts,key=cv2.contourArea)
for eps in [2,3,4]:
    ap=cv2.approxPolyDP(cv2.convexHull(c),eps,True).reshape(-1,2)+[610,370]
    print(R,'eps',eps,ap.tolist())
print('area',m.sum())
vis=cv2.resize(im[370:450,610:700],None,fx=6,fy=6,interpolation=cv2.INTER_CUBIC)
cv2.drawContours(vis,[c*6],-1,(0,0,255),1)
cv2.imwrite(f'book_mask_{R}.png',vis)
