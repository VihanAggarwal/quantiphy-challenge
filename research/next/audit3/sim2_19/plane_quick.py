import cv2, numpy as np, sys
from common import *
for v in ['simulation_0284','simulation_0286','simulation_0285','simulation_0287']:
    fr=frames(v)
    n=len(fr)
    bg=np.median(np.stack([fr[i] for i in range(0,n,3)]),axis=0).astype(np.int16)
    res=[]
    for i in range(n):
        d=np.abs(fr[i].astype(np.int16)-bg).max(axis=2)
        m=(d>30).astype(np.uint8)
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if nl<2: res.append(None); continue
        k=1+np.argmax(st[1:,4])
        x,y,w,h,a=st[k]
        res.append((i,x,y,w,h,a,cen[k][0],cen[k][1]))
    print(v,n)
    for r in res[::6]: print('  ',r)
