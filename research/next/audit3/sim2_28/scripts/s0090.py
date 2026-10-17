import sys; sys.path.insert(0,'scripts')
from vid import frames
import cv2, numpy as np
F=[f.astype(np.float32) for f in frames('simulation_0090')]
bg=np.median(np.stack(F[20:30]),axis=0)
bg=cv2.GaussianBlur(bg,(5,5),0)
for i in range(0,21):
    d=np.abs(F[i]-bg).max(axis=2)
    m=(d>12).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    comps=[(st[k],cen[k]) for k in range(1,n) if st[k][4]>50]
    comps.sort(key=lambda c:c[0][0])
    print(i,[ (int(s[0]),int(s[0]+s[2]),int(s[1]),int(s[1]+s[3]),int(s[4]), round(c[0],1),round(c[1],1)) for s,c in comps])
