import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/audit3/sim2_08')
from util import *
v=sys.argv[1]
fr=frames(v)
last=cv2.GaussianBlur(fr[-1],(3,3),0).astype(int)
for n in range(0,40):
    f=cv2.GaussianBlur(fr[n],(3,3),0).astype(int)
    d=np.abs(f-last).sum(axis=2)
    m=(d>60).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
    out=[tuple(int(t) for t in st[i]) for i in range(1,nl) if st[i][4]>80]
    print(n,out)
