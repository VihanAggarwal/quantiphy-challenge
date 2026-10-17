import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/audit3/sim2_26/scripts')
from util import *
F=frames('0160')
bg=np.median(np.stack(F[2:]),axis=0)
xs=[]
for i,f in enumerate(F):
    d=np.abs(f.astype(float)-bg).sum(2)
    m=(d>60).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: xs.append(np.nan); continue
    k=1+np.argmax(st[1:,4])
    xs.append(cen[k][0])
    print(i,st[k],np.round(cen[k],1))
xs=np.array(xs)
print(np.round(np.diff(xs),1))
