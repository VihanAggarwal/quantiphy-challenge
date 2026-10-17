import sys; sys.path.insert(0,'scripts')
from vid import frames
import cv2, numpy as np
F=frames('internet_0008_segmented')
out=[]
for i,f in enumerate(F):
    m=(255-f.min(axis=2)>60).astype(np.uint8)
    m[505:,700:]=0  # watermark
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    comps=[(st[k],cen[k]) for k in range(1,n) if st[k][4]>15]
    if i%20==0 or i>=200:
        print(i,[(int(s[0]),int(s[0]+s[2]),int(s[1]),int(s[1]+s[3]),int(s[4]),round(c[0],1)) for s,c in comps])
