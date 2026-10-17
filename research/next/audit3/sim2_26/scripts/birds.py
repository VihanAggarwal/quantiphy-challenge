import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/audit3/sim2_26/scripts')
from util import *
F=frames('0088')
sky=np.median(np.stack(F[::3]),axis=0)
for i,f in enumerate(F):
    d=np.abs(f.astype(float)-sky).sum(2)
    m=(d>60).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    comps=[(st[k,cv2.CC_STAT_AREA],st[k,0],st[k,1],st[k,2],st[k,3],cen[k]) for k in range(1,n) if st[k,cv2.CC_STAT_AREA]>200]
    comps.sort(key=lambda c:c[1])
    print(i,[(a,x,y,w,h,round(c[0],1),round(c[1],1)) for a,x,y,w,h,c in comps])
