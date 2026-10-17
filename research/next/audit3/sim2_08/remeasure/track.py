from util import *
import sys
for v in ['0257','0258','0259','0260']:
    F=frames(v)
    last=F[-1].astype(np.int16)
    print('clip',v,len(F))
    for i in range(0,22):
        d=np.abs(F[i].astype(np.int16)-last).max(2)
        m=(d>40).astype(np.uint8)
        m[870:,:]=0  # ignore table and below
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n<2: print(i,'none'); continue
        k=1+np.argmax(st[1:,4])
        x,y,w,h,a=st[k]
        print(i,'bbox x%d-%d y%d-%d w%d h%d area%d cen(%.1f,%.1f)'%(x,x+w,y,y+h,w,h,a,cen[k][0],cen[k][1]))
