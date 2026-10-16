import sys, cv2, numpy as np; sys.path.insert(0,'scripts')
from geo import *
# silhouette from x render (median over frames)
ms=[]
for n in range(0,48,4):
    im=cv2.imread(f'frames/x_{n:02d}.png').astype(int)
    ms.append(~((im[...,1]>200)&(im[...,2]<80)&(im[...,0]<80)))
m=(np.mean(ms,0)>0.5).astype(np.uint8)
sub=np.zeros_like(m); sub[560:670,610:720]=m[560:670,610:720]
cs,_=cv2.findContours(sub,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
c=max(cs,key=cv2.contourArea)
print('area',cv2.contourArea(c))
rect=cv2.minAreaRect(c); print('minAreaRect',rect)
eps=2.0
ap=cv2.approxPolyDP(c,eps,True).reshape(-1,2); print('approx poly',ap.tolist())
# fit 4 lines to contour via quadrilateral: use cv2.approxPolyDP with increasing eps until 4 pts
for e in np.arange(1,15,0.5):
    ap=cv2.approxPolyDP(c,e,True)
    if len(ap)==4: break
quad=ap.reshape(-1,2).astype(float); print('quad eps',e,quad.tolist())
np.save('book_quad.npy',quad)
