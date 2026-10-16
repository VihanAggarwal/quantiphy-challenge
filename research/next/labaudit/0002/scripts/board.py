import cv2, numpy as np
f=cv2.imread('frames/f48.png')
hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV).astype(int)
m=((hsv[...,1]<40)&(hsv[...,2]>200)).astype(np.uint8)
n,lab,st,cen=cv2.connectedComponentsWithStats(m)
k=1+np.argmax(st[1:,4]); print('board bbox',st[k])
B=(lab==k)
cv2.imwrite('boardmask.png',B.astype(np.uint8)*255)
ys=np.nonzero(B.any(1))[0]
for y in list(range(ys.min(),ys.min()+6))+list(range(ys.min()+10,ys.max(),15))+list(range(ys.max()-5,ys.max()+1)):
    xs=np.nonzero(B[y])[0]; print(y,xs.min(),xs.max(),xs.max()-xs.min()+1)
xs=np.nonzero(B.any(0))[0]
for x in list(range(xs.min(),xs.min()+5))+list(range(xs.min()+10,xs.max(),15))+list(range(xs.max()-4,xs.max()+1)):
    yy=np.nonzero(B[:,x])[0]; print('x',x,yy.min(),yy.max())
