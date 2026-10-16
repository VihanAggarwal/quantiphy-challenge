import cv2, numpy as np
from common import *
o=load('')
med=np.median(o[::3].astype(float),0).astype(np.uint8)
cv2.imwrite(O+'median_o.jpg',med,[cv2.IMWRITE_JPEG_QUALITY,92])
g=cv2.cvtColor(med,cv2.COLOR_BGR2GRAY)
lsd=cv2.createLineSegmentDetector(0)
L=lsd.detect(g)[0].reshape(-1,4)
segs=[]
for x1,y1,x2,y2 in L:
    dx,dy=x2-x1,y2-y1; ln=np.hypot(dx,dy)
    if ln<60: continue
    ang=np.degrees(np.arctan2(abs(dx),abs(dy)))
    if ang<25: segs.append((x1,y1,x2,y2,ln,ang))
segs=np.array(segs)
print(len(segs))
vis=med.copy()
for i,s in enumerate(segs):
    cv2.line(vis,(int(s[0]),int(s[1])),(int(s[2]),int(s[3])),(0,0,255),2)
    cv2.putText(vis,str(i),(int((s[0]+s[2])/2),int((s[1]+s[3])/2)),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),1)
    print(i,np.round(s,1))
cv2.imwrite(O+'vlines.jpg',vis,[cv2.IMWRITE_JPEG_QUALITY,90])
np.save(O+'vsegs.npy',segs)
