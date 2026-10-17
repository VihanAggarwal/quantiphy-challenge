import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/audit3/sim2_08')
from util import *
v=sys.argv[1]
fr=frames(v)
last=cv2.GaussianBlur(fr[-1],(3,3),0).astype(int)
rows=[]
for n in range(0,18):
    f=cv2.GaussianBlur(fr[n],(3,3),0).astype(int)
    d=np.abs(f-last).sum(axis=2)
    m=(d>60).astype(np.uint8)
    m[870:,:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if nl<=1: rows.append((n,None)); continue
    i=1+np.argmax(st[1:,cv2.CC_STAT_AREA])
    x,y,w,h,a=st[i]
    rows.append((n,(x,y,w,h,a,cen[i][0],cen[i][1])))
for n,r in rows: print(n,r)
