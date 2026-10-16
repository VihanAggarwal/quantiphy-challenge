import cv2, numpy as np
from common import *
med=cv2.imread(O+'median_o.jpg')
g=cv2.cvtColor(med,cv2.COLOR_BGR2GRAY)
lsd=cv2.createLineSegmentDetector(0)
L=lsd.detect(g)[0].reshape(-1,4)
segs=[]
for x1,y1,x2,y2 in L:
    dx,dy=x2-x1,y2-y1; ln=np.hypot(dx,dy)
    if ln<50: continue
    if max(x1,x2)<850 and max(y1,y2)>250: continue
    segs.append((x1,y1,x2,y2,ln,np.degrees(np.arctan2(dy,dx))))
segs=np.array(segs)
vis=med.copy()
for i,s in enumerate(segs):
    cv2.line(vis,(int(s[0]),int(s[1])),(int(s[2]),int(s[3])),(0,0,255),2)
    cv2.putText(vis,str(i),(int((s[0]+s[2])/2),int((s[1]+s[3])/2)),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),1)
    print(i,np.round(s,1))
cv2.imwrite(O+'lines2.jpg',vis,[cv2.IMWRITE_JPEG_QUALITY,90])
np.save(O+'segs2.npy',segs)
