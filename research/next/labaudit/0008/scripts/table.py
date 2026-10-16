import cv2, numpy as np
F='/home/user/quantiphy-challenge/research/next/labaudit/0008/'
im=cv2.imread(F+'frames/captured_0008_f10.png')
hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV).astype(int)
lab=cv2.cvtColor(im,cv2.COLOR_BGR2LAB).astype(int)
# sample wood colour inside table
p=hsv[460:520,560:640].reshape(-1,3); print('wood hsv med',np.median(p,0), 'lab', np.median(lab[460:520,560:640].reshape(-1,3),0))
m=(abs(hsv[...,0]-np.median(p[:,0]))<=6)&(hsv[...,1]>60)&(hsv[...,1]<170)&(hsv[...,2]>130)
m=m.astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
n,l,st,cen=cv2.connectedComponentsWithStats(m)
k=l[490,600]; mk=(l==k).astype(np.uint8)*255
mk=cv2.morphologyEx(mk,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
cv2.imwrite(F+'tablemask.png',mk)
cs,_=cv2.findContours(mk,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
c=max(cs,key=cv2.contourArea)
ap=cv2.approxPolyDP(c,8,True); print('approx poly',ap.reshape(-1,2).tolist())
print('area',cv2.contourArea(c))
